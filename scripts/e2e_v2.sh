#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
SUFFIX="$(date +%s)"

preflight() {
  if ! curl -fsS "${BASE_URL}/health" >/dev/null 2>&1; then
    echo "Backend is not reachable at ${BASE_URL}."
    echo "Start it first (example): docker compose up -d db backend"
    exit 1
  fi
}

req() {
  local method="$1"
  local path="$2"
  local body="${3:-}"
  local token="${4:-}"

  local headers=(-H "Content-Type: application/json")
  if [[ -n "$token" ]]; then
    headers+=(-H "Authorization: Bearer $token")
  fi

  if [[ -n "$body" ]]; then
    curl -sS -X "$method" "${BASE_URL}${path}" "${headers[@]}" -d "$body"
  else
    curl -sS -X "$method" "${BASE_URL}${path}" "${headers[@]}"
  fi
}

json_get() {
  local key="$1"
  python3 -c "import json,sys; print(json.load(sys.stdin)['$key'])"
}

otp_login() {
  local role="$1"
  local phone="$2"
  local name="$3"
  local otp_resp

  otp_resp="$(req POST /api/auth/otp/request "{\"phone\":\"${phone}\",\"role\":\"${role}\",\"name\":\"${name}\"}")"
  if ! printf '%s' "$otp_resp" | python3 -c 'import json,sys; json.load(sys.stdin);' >/dev/null 2>&1; then
    echo "OTP request failed. Response:"
    printf '%s\n' "$otp_resp"
    exit 1
  fi
  local otp_code
  otp_code="$(printf '%s' "$otp_resp" | json_get otp || true)"
  if [[ -z "${otp_code}" ]]; then
    echo "OTP_EXPOSE_IN_RESPONSE appears disabled; e2e needs demo OTP exposure."
    echo "Set OTP_EXPOSE_IN_RESPONSE=1 for local/dev runs."
    exit 1
  fi

  req POST /api/auth/otp/verify "{\"phone\":\"${phone}\",\"role\":\"${role}\",\"otp\":\"${otp_code}\"}" | json_get access_token
}

preflight
echo "Running V2 E2E against ${BASE_URL}"

SUFFIX_TAIL="${SUFFIX: -6}"
ADMIN_PHONE="9000000001"
SUP_PHONE="9110${SUFFIX_TAIL}"
BUYER_PHONE="9220${SUFFIX_TAIL}"

ADMIN_TOKEN="$(otp_login admin "${ADMIN_PHONE}" "Admin V2 E2E")"
SUP_TOKEN="$(otp_login supplier "${SUP_PHONE}" "Supplier V2 E2E")"
BUYER_TOKEN="$(otp_login user "${BUYER_PHONE}" "Buyer V2 E2E")"

SUP_PROFILE="$(req POST /api/v2/suppliers/profile "{\"business_name\":\"V2 E2E Materials\",\"phone\":\"9876543210\",\"address\":\"Industrial Area\"}" "$SUP_TOKEN")"
SUP_ID="$(printf '%s' "$SUP_PROFILE" | json_get id)"

req POST /api/v2/suppliers/me/documents "{\"doc_type\":\"AADHAR\",\"file_url\":\"https://example.com/aadhar.png\"}" "$SUP_TOKEN" >/tmp/e2e_v2_doc.json

req POST "/api/v2/suppliers/${SUP_ID}/verify" "" "$ADMIN_TOKEN" >/tmp/e2e_v2_verify.json

BOOKING="$(req POST /api/v2/bookings "{\"supplier_id\":${SUP_ID},\"description\":\"Need 20 tons of aggregates\"}" "$BUYER_TOKEN")"
printf '%s' "$BOOKING" >/tmp/e2e_v2_booking.json
BOOKING_ID="$(printf '%s' "$BOOKING" | json_get id)"

req POST "/api/v2/bookings/${BOOKING_ID}/accept" "" "$SUP_TOKEN" >/tmp/e2e_v2_accept.json

python3 - <<'PY'
import json

verified = json.load(open("/tmp/e2e_v2_verify.json"))
booking = json.load(open("/tmp/e2e_v2_booking.json"))
accepted = json.load(open("/tmp/e2e_v2_accept.json"))

assert verified.get("status") == "VERIFIED"
assert booking.get("status") == "PENDING_SUPPLIER_APPROVAL"
assert accepted.get("status") == "ACCEPTED"
print("e2e_v2_ok")
PY

echo "v2_supplier_id=${SUP_ID} v2_booking_id=${BOOKING_ID}"
