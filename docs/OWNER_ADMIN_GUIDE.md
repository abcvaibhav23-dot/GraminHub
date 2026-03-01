# GraminHub — Owner/Admin Operational Guide (Production)

This guide is for the **Owner/Admin** operating GraminHub in production. It focuses on day‑to‑day ops, safety controls, verification, and incident handling.

## 1) Admin Access (Strict)

- Admin OTP login is enabled **only** for allowlisted phone numbers:
  - `ADMIN_PHONE_ALLOWLIST=91XXXXXXXXXX,91YYYYYYYYYY`
- Production must keep:
  - `OTP_EXPOSE_IN_RESPONSE=0`
  - `OTP_DELIVERY_MODE` configured to a real provider (not `console`)

How to login as Owner/Admin (production):
1. Open `/login`
2. Select role **Admin (Owner/Admin)**
3. Enter allowlisted phone → request OTP → verify OTP
4. You will be redirected to `/admin-dashboard`

## 2) Daily Checklist (10 minutes)

1. **Health check**
   - `GET /health` returns `status=ok`
2. **New suppliers pending review**
   - Review newly submitted supplier profiles/documents.
3. **Bookings overview**
   - Look for abnormal spikes, repeated cancellations, disputes, or suspicious patterns.
4. **Support channel**
   - Check WhatsApp/phone support queue and resolve top issues first.

## 3) Supplier Verification Workflow (Recommended)

Target: verify suppliers that are **real**, reachable, and accurately listed.

### A) Review checklist

- Phone reachable (call once)
- Business name and address look realistic
- Category/services match what they can deliver
- Pricing looks sensible and matches the correct unit type (example: vehicles should be `per_trip`/`per_day`, materials often `per_bag`/`per_kg`)
- Document checks (as applicable):
  - ID proof (Aadhaar/other)
  - Business proof (if needed)
  - Any local license/permit (if applicable for your area)

### B) Approve / Reject rules

Approve when:
- Supplier is reachable and details are consistent
- Documents are present and not obviously forged

Reject when:
- Phone unreachable after multiple attempts
- Mismatched documents / suspicious identity
- Fraud complaints or repeated bad behavior

### C) Post-approval expectations

- Supplier listing becomes visible in search and on category-wise homepage lists.
- Supplier must keep phone number active; repeated unreachable incidents → suspend.

## 4) Account Controls (Block/Suspend)

Use block/suspend for:
- Fraud reports
- Wrong pricing bait (price mismatch at delivery)
- Harassment, abuse, or scam attempts

Operational approach:
- First offense: warn + note + temporary suspension (recommended)
- Repeated offense: long suspension or permanent block

## 5) Platform Safety Controls (Owner Settings)

Maintain simple “kill switches”:

- Disable supplier WhatsApp if spam/fraud spikes
- Disable supplier call visibility if misuse occurs
- Enforce rate limits on OTP and public endpoints

Recommendation:
- Keep any emergency toggle changes documented (date/time/reason).

## 6) Customer Support Playbook (Rural-first)

When a buyer complains:
- Confirm supplier phone number and booking details
- Ask for screenshot of WhatsApp chat (if available)
- If supplier is at fault repeatedly → suspend supplier and re-verify

When a supplier complains:
- Confirm listing data, category, phone formatting, visibility
- Check whether supplier is verified/approved

## 7) Incident Response

### A) OTP abuse / suspicious login attempts

Actions:
- Reduce OTP issuance by tightening rate limits
- Temporarily increase resend interval
- If needed: disable OTP issuance for certain patterns (future enhancement)

### B) Data leak suspicion

Actions:
- Rotate `JWT_SECRET_KEY`
- Audit access logs and DB access
- Restrict CORS origins

### C) Broken deployment

Actions:
- Roll back to last known good image/version
- Verify DB migrations state
- Run a minimal smoke test: login → search → call/WhatsApp → admin page

## 8) Releases & Migrations (Production Discipline)

Production should use migration-first schema management:

- `DB_BOOTSTRAP_MODE=migrations`
- Apply migrations before starting:
  - `alembic upgrade head`

Release checklist:
- Backup DB
- Apply migrations
- Deploy backend
- Smoke test (buyer + supplier + admin)
- Monitor logs for 30 minutes

## 9) Backups (Recommended Minimum)

- Daily automated Postgres backups (retain at least 7–14 days)
- Test restore monthly (to a staging DB)

## 10) Secrets & Config Hygiene

- Never commit `.env`
- Use strong secrets:
  - `JWT_SECRET_KEY` (long random)
  - OTP webhook tokens (if used)
- Set `CORS_ORIGINS` to only your real domains
