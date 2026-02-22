#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
SUFFIX="$(date +%s)"

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

echo "Running E2E against ${BASE_URL}"

ADMIN_EMAIL="admin_${SUFFIX}@example.com"
ADMIN_PASS="secret123"
req POST /api/auth/register "{\"name\":\"Admin E2E\",\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASS}\",\"role\":\"admin\"}" >/tmp/e2e_admin_reg.json
ADMIN_TOKEN="$(req POST /api/auth/login "{\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASS}\"}" | json_get access_token)"

SUP_EMAIL="supplier_${SUFFIX}@example.com"
SUP_PASS="secret123"
req POST /api/auth/register "{\"name\":\"Supplier E2E\",\"email\":\"${SUP_EMAIL}\",\"password\":\"${SUP_PASS}\",\"role\":\"supplier\"}" >/tmp/e2e_supplier_reg.json
SUP_TOKEN="$(req POST /api/auth/login "{\"email\":\"${SUP_EMAIL}\",\"password\":\"${SUP_PASS}\"}" | json_get access_token)"

SUP_PROFILE="$(req POST /api/suppliers/profile "{\"business_name\":\"E2E Materials\",\"phone\":\"9876543210\",\"address\":\"Industrial Area\"}" "$SUP_TOKEN")"
SUP_ID="$(printf '%s' "$SUP_PROFILE" | json_get id)"
req POST /api/suppliers/services "{\"category_id\":1,\"price\":1500,\"availability\":\"in stock\"}" "$SUP_TOKEN" >/tmp/e2e_service.json

req POST "/api/admin/suppliers/${SUP_ID}/approve" "" "$ADMIN_TOKEN" >/tmp/e2e_approve.json

USER_EMAIL="user_${SUFFIX}@example.com"
USER_PASS="secret123"
req POST /api/auth/register "{\"name\":\"User E2E\",\"email\":\"${USER_EMAIL}\",\"password\":\"${USER_PASS}\",\"role\":\"user\"}" >/tmp/e2e_user_reg.json
USER_TOKEN="$(req POST /api/auth/login "{\"email\":\"${USER_EMAIL}\",\"password\":\"${USER_PASS}\"}" | json_get access_token)"

SEARCH="$(req GET '/api/suppliers/search?category_id=1')"
printf '%s' "$SEARCH" >/tmp/e2e_search.json

BOOKING="$(req POST /api/bookings "{\"supplier_id\":${SUP_ID},\"description\":\"Need 20 tons of aggregates\"}" "$USER_TOKEN")"
printf '%s' "$BOOKING" >/tmp/e2e_booking.json
BOOKING_ID="$(printf '%s' "$BOOKING" | json_get id)"

WA_BOOKING="$(req POST /api/bookings/whatsapp "{\"supplier_id\":${SUP_ID},\"description\":\"Need tipper vehicle tomorrow morning\"}" "$USER_TOKEN")"
printf '%s' "$WA_BOOKING" >/tmp/e2e_wa_booking.json
WA_URL="$(printf '%s' "$WA_BOOKING" | json_get whatsapp_url)"

GUEST_WA_BOOKING="$(req POST /api/bookings/guest/whatsapp "{\"supplier_id\":${SUP_ID},\"description\":\"Need rental without login\",\"guest_name\":\"Guest Lead\",\"guest_phone\":\"9000000000\"}")"
printf '%s' "$GUEST_WA_BOOKING" >/tmp/e2e_guest_wa_booking.json

CALL="$(req POST "/api/suppliers/${SUP_ID}/call" "" "$USER_TOKEN")"
printf '%s' "$CALL" >/tmp/e2e_call.json
PHONE="$(printf '%s' "$CALL" | json_get phone)"

SUP_BOOKINGS="$(req GET /api/suppliers/me/bookings "" "$SUP_TOKEN")"
printf '%s' "$SUP_BOOKINGS" >/tmp/e2e_supplier_bookings.json
ADMIN_BOOKINGS="$(req GET /api/admin/bookings "" "$ADMIN_TOKEN")"
printf '%s' "$ADMIN_BOOKINGS" >/tmp/e2e_admin_bookings.json

python3 - <<'PY'
import json

search = json.load(open("/tmp/e2e_search.json"))
booking = json.load(open("/tmp/e2e_booking.json"))
wa_booking = json.load(open("/tmp/e2e_wa_booking.json"))
guest_wa_booking = json.load(open("/tmp/e2e_guest_wa_booking.json"))
call = json.load(open("/tmp/e2e_call.json"))
supplier_bookings = json.load(open("/tmp/e2e_supplier_bookings.json"))
admin_bookings = json.load(open("/tmp/e2e_admin_bookings.json"))

assert isinstance(search, list) and len(search) >= 1
assert booking.get("status") == "pending"
assert wa_booking.get("status") == "pending"
assert "wa.me/" in wa_booking.get("whatsapp_url", "")
assert guest_wa_booking.get("status") == "pending"
assert "wa.me/" in guest_wa_booking.get("whatsapp_url", "")
assert call.get("phone")
assert isinstance(supplier_bookings, list) and len(supplier_bookings) >= 1
assert isinstance(admin_bookings, list) and len(admin_bookings) >= 1
print("e2e_ok")
PY

echo "supplier_id=${SUP_ID} booking_id=${BOOKING_ID} phone=${PHONE} whatsapp=${WA_URL}"
