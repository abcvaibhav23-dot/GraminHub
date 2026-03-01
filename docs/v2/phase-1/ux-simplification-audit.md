# GraminHub v1 → v2 (Phase 1) — UX Simplification Report (Rural-First)

Date: 2026-02-28

Scope:
- Live site spot-check: `https://www.graminhub.in/` home + `/login` page render.
- Local templates: `GraminHub/backend/app/templates/*` (notably `login.html`).

## UX Goals (v2)

- One action per screen (reduce cognitive load).
- Large tap targets, high contrast, minimal copy.
- Hindi-first with simple English fallback (toggle).
- Guided flows (stepper-style): “Choose → Call/Book → Track”.
- Prominent “Call Supplier” and “WhatsApp” primary actions.
- Visual status badges (booking/supplier lifecycle).
- Mobile-first; low bandwidth friendly (optimize images, defer heavy JS).

## Observed v1 UX Patterns (What’s Working)

- Login screen is visually polished and mobile-friendly.
- OTP-based login is already the primary path (good for villagers).
- Home is category-driven, with search and supplier cards.
- Support section includes phone/WhatsApp contact (important for rural trust).

## Observed v1 UX Complexity / Confusion Risks

1. **Tabbed “page-inside-page” navigation**
   - Home, supplier, and admin dashboards use nested tabs (multiple levels).
   - For low digital literacy users, nested tabs increase “lost” feeling and reduce task completion.

2. **Too much information per screen**
   - Hero sections + stats + bullet points + multi-input forms can overwhelm.
   - Rural-first should reduce competing UI elements and prioritize next action.

3. **Login role selection**
   - OTP login includes a role dropdown (User/Supplier/Admin).
   - This can confuse users and is error-prone (“logged in with wrong role”).
   - v2 should infer role where possible (or provide a clearer “I am Buyer / I am Supplier” split as first step).

4. **Long text and mixed-language density**
   - Some screens mix Hindi + English + technical terms.
   - v2 should standardize plain Hindi labels and keep English as optional assistive text.

5. **Booking visibility**
   - “WhatsApp booking” is convenient, but users need a clear “Track my booking” screen even if WhatsApp used.

## v2 Simplified Screen Map (Template UI Structure)

Buyer flow:
1. **Home (Categories first)**: big category tiles + one search box
2. **Search results**: simple supplier/listing cards
3. **Listing details**: image, price, location, two primary buttons: Call / Book
4. **Book**: minimal fields + confirm
5. **Booking status**: badge + next action (call/extend/cancel)

Supplier flow:
1. **Welcome**: “Complete Verification” / “See Booking Requests”
2. **Verification**: document upload in 1–2 steps
3. **Booking requests**: big Accept / Reject buttons
4. **Active jobs**: start / complete action buttons
5. **Earnings**: simple totals and payout status

Admin flow:
1. **Dashboard**: KPIs + alerts
2. **Supplier approvals**: list + approve/reject with reasons
3. **Bookings oversight**: states + dispute flags
4. **Commission & plans**: tenant-aware configuration

## Rural UX Notes (Concrete UI Requirements)

- Buttons: minimum 48px height; primary actions always visible above fold.
- Forms: phone-only OTP login, avoid email unless needed.
- Copy: use verbs (“Call”, “Book”, “Track”) not nouns.
- Feedback: confirm actions with a single large toast + status badge.
- Errors: show one clear instruction (“OTP गलत है, फिर से OTP लें”).
- Offline/low network: show retry button; keep pages light.

## Implementation Guidance (v2 Templates)

- Replace nested tab dashboards with route-per-task pages:
  - `/supplier/verification`, `/supplier/bookings`, `/supplier/earnings`
  - `/admin/suppliers/pending`, `/admin/bookings`, `/admin/disputes`
- Add language toggle at top-right; store preference in cookie/localStorage.
- Use consistent status chips:
  - Booking: Created / Pending Approval / Accepted / In Progress / Completed / Cancelled / Disputed / Resolved
  - Supplier: Registered / Docs Submitted / Under Review / Verified / Rejected / Suspended

