# GraminHub — UI Verification Checklist (Laptop + Mobile)

Use this checklist after UI/template changes to confirm alignment, readability, and rural-first usability.

## 1) Viewports to test

- Mobile (small): 360×800 (Android) / 390×844 (iPhone)
- Tablet: 768×1024
- Laptop: 1366×768
- Desktop: 1440×900 or 1920×1080

## 2) Pages to verify

- Home: `/`
- Login: `/login`
- Register: `/register`
- Supplier dashboard: `/supplier-dashboard`
- Admin dashboard: `/admin-dashboard`

## 3) Global UI checks (all pages)

- Header fits in one row on laptop; wraps cleanly on mobile.
- Language toggle switches **Hindi ↔ English** and stays consistent across page navigation.
- Buttons are easy to tap (>= 48px height) on mobile.
- Text contrast is readable under sunlight (no light gray on white).
- No horizontal scrolling on mobile.

## 4) Home page checks (v2)

- Search is visible at top:
  - String search works (type + Search)
  - Voice search works (permission prompt shows; recognized text appears)
- If AI Search is enabled (`AI_SEARCH_ENABLED=1`):
  - “Ask AI/AI मदद” button is visible next to Search/Voice
  - AI panel opens, shows answer, and “Use suggested search” triggers a normal search
- “Available now” section is split into 3 columns on laptop:
  - Vehicle
  - Building Materials
  - Coming Soon
- Each column shows 2–3 top items and card layout is aligned.
- Search results section renders correctly and does not break alignment.

## 5) Login checks

- Phone field and OTP fields align and are usable on mobile.
- OTP request and verify show clear success/failure messages.
- Demo-only hints are hidden when `SHOW_DEMO_HINTS=0`.

## 5.1) Supplier listing checks

- Supplier Dashboard item form:
  - “Price unit/type” dropdown exists and is usable on mobile
  - Price renders on Home cards as `₹X / unit` (example: `₹1200 / per trip`)

## 6) Common UX issues to catch

- Mixed language labels on the same button (unless intentional brand words like WhatsApp).
- Too much text above the fold on mobile.
- Cards not aligned (different heights with broken spacing).
- Missing icons/images causing layout jump.
