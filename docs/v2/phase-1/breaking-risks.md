# GraminHub v1 → v2 (Phase 1) — Breaking Risks & Mitigations

Date: 2026-02-28

This document lists the most likely “break points” when moving from v1 MVP to v2 Clean Architecture, plus the mitigation strategy to keep core flows functional.

## 1) Authentication / Login

Risk:
- v1 OTP login auto-creates users using phone+role; role is stored on the user row and embedded in JWT.

Break symptoms:
- Users “lose access” if identity mapping changes.
- Supplier accounts may not match bookings if user IDs change.

Mitigation:
- Introduce v2 `auth_identities` table to map `phone` (and later email) to a single `user_id` per tenant.
- Provide a migration path that preserves existing user IDs and roles, then progressively deprecate synthetic OTP emails.
- Keep a v1 compatibility login mode during cutover (feature flag).

## 2) Booking Flow

Risk:
- v1 booking status is a string; there is no event log or legal transition enforcement.

Break symptoms:
- Old bookings stuck in unknown status.
- Supplier dashboards showing wrong booking state.

Mitigation:
- Map v1 statuses to v2 state enum on migration.
- Create an initial `booking_events` backfill event (“IMPORTED”) for existing records.
- Implement state machine with strict transitions; treat unknown legacy values as `CREATED` or `PENDING_SUPPLIER_APPROVAL` based on heuristics.

## 3) Supplier Verification

Risk:
- v1 uses booleans (`approved`, `blocked`, `featured`).

Break symptoms:
- Approved suppliers may become invisible if mapping is wrong.

Mitigation:
- Replace with lifecycle enum; map `(approved=true, blocked=false)` → `VERIFIED`, `(approved=false, blocked=false)` → `UNDER_REVIEW` (or `REGISTERED` if docs missing), `(blocked=true)` → `SUSPENDED`.
- Add admin audit entries for all imported state mappings.

## 4) Schema / Migrations

Risk:
- v1 mutates schema at startup with raw SQL; v2 will use Alembic migrations.

Break symptoms:
- Deployments fail due to missing columns or partially applied schema.

Mitigation:
- Remove runtime DDL from startup and replace with explicit migrations.
- Enforce `alembic_version` and a migration playbook in README.

## 5) Authorization

Risk:
- v1 uses route-level `require_roles` checks; v2 requires policy engine with object-level checks.

Break symptoms:
- Legitimate users blocked; privilege escalation if policies missed.

Mitigation:
- Build policies first and write tests around them (golden-path + negative tests).
- Add a temporary “compat” guard layer while policies are rolled out per domain.

## 6) Multi-tenancy (SaaS)

Risk:
- Adding `tenant_id` to major tables affects every query.

Break symptoms:
- Data leaks across tenants if scoping is inconsistent.

Mitigation:
- Add `tenant_id` with default tenant “graminhub” for v1 data.
- Enforce tenant scoping in repository layer only (single source of truth).
- Add tests asserting tenant isolation (cannot fetch/update cross-tenant).

## 7) UI / Templates

Risk:
- Major UI simplification can remove features users rely on (even if confusing).

Break symptoms:
- Users cannot find dashboards or bookings.

Mitigation:
- Preserve key URLs with redirects (e.g., `/supplier-dashboard` → `/supplier/bookings`).
- Introduce a minimal “Help” page and support CTA on every screen.

