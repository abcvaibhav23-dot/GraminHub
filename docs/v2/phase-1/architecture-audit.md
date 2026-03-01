# GraminHub v1 → v2 (Phase 1) — Architecture Audit Report

Date: 2026-02-28

Scope:
- Local repo: `GraminHub/backend/app/*`
- Live site spot-check: `https://www.graminhub.in/` (home + login pages rendered)

## Executive Summary

GraminHub v1 is a functional MVP with a single FastAPI app serving both Jinja2 UI and JSON APIs. It has basic service separation (`api/`, `services/`, `models/`, `schemas/`, `core/`) and a working OTP login flow. However, it is not production-grade for a SaaS future: it lacks clean domain boundaries, normalized RBAC/policy enforcement, auditability, state machines for booking/supplier lifecycles, migration discipline, and tenant scoping. Several security and scalability risks exist (notably schema mutation at startup, in-memory rate limiting, and permissive role handling).

The v2 redesign should be a deliberate greenfield refactor into Clean Architecture with domain modules, policy-based authorization, explicit state machines, and migration-driven database evolution. The UI should become “rural-first” and flow-driven.

## Current v1 Structure (Observed)

- Entry: `GraminHub/backend/app/main.py`
- Layers:
  - Routes: `GraminHub/backend/app/api/*`
  - Services: `GraminHub/backend/app/services/*`
  - Models: `GraminHub/backend/app/models/*` (SQLAlchemy)
  - Schemas: `GraminHub/backend/app/schemas/*` (Pydantic)
  - Core: `GraminHub/backend/app/core/*` (config, security, exceptions, logging)
  - UI: `GraminHub/backend/app/templates/*`, `GraminHub/backend/app/static/*`
- Auth:
  - JWT bearer with `role` embedded in token (`GraminHub/backend/app/core/security.py`)
  - OTP challenge stored in DB (`GraminHub/backend/app/models/otp_challenge.py`)
  - “OTP auto-user creation” for phone+role identities (`GraminHub/backend/app/services/user_service.py`)

## Architecture Flaws / Tight Coupling

1. **Schema mutation in app startup**
   - `GraminHub/backend/app/main.py` performs ad-hoc DDL (`ALTER TABLE`, `CREATE INDEX`) at runtime.
   - Risks: non-repeatable deployments, race conditions in multi-instance, fragile logic across DBs, and no migration history.

2. **Cross-cutting concerns live in the app entrypoint**
   - Rate limiting, request ID, DDL, seeding, and templates are all wired in `main.py`, making it a “god file”.

3. **Role & permission logic is not centralized**
   - `require_roles(...)` is route-level and role-string based.
   - There is no policy engine; services don’t enforce access rules consistently, and “role” is not normalized.

4. **Domain boundaries are implicit, not enforced**
   - “Supplier”, “Booking”, “Auth”, “Admin” are not isolated as independent domain modules with defined ports/adapters.

5. **Business flows are missing explicit state machines**
   - Booking status is a free string (`Booking.status`) without legal transition control.
   - Supplier verification is a boolean `approved` + boolean `blocked`, which cannot represent a lifecycle.

6. **SaaS readiness is absent**
   - No `tenant_id` scoping; no tenant-aware repositories; no isolation strategy (row-level tenancy).

## Database Design Issues (v1)

1. **Boolean status flags**
   - `Supplier.approved`, `Supplier.blocked`, `Supplier.featured` are booleans.
   - v2 requirement: no boolean status fields; use enums / state.

2. **Unconstrained status strings**
   - `Booking.status` is `String(30)` with default `"pending"`.
   - Missing: enum constraint, transition log, and indexes for state queries.

3. **Missing core entities for scale**
   - No tables for `roles`, `booking_events`, `audit_logs`, `tenants`, `subscription_plans`, `payments`, `commissions`.

4. **Weak multi-identity modelling**
   - OTP login creates “role-scoped” users with synthetic emails (`otp.<role>.<phone>@...`), which is pragmatic for MVP but complicates identity management and SaaS user lifecycle.

## Scalability / Reliability Risks

1. **In-memory rate limiting**
   - `rate_buckets` dict in `GraminHub/backend/app/main.py` is per-process and resets on restart; not safe across workers/instances.

2. **Seeding and schema modification on every startup**
   - Increases startup time and introduces non-determinism.

3. **Template + API in one runtime**
   - Fine for MVP, but operationally the UI and API lifecycles become coupled (deploys, caching, auth, headers).

## Security Risks / Gaps (v1)

1. **Token storage (browser localStorage)**
   - The login UI explicitly stores token in localStorage (XSS impact becomes account takeover).
   - v2 should use httpOnly cookies (or short-lived access + refresh rotation) depending on deployment.

2. **JWT role is trusted from token**
   - Current auth layer uses `role` from decoded token and checks role strings. If token secret leaks, privilege escalation is trivial.
   - v2 should use user/role data from DB and a policy engine; tokens should identify subject + tenant + session.

3. **Ad-hoc DDL increases blast radius**
   - Mistakes in DDL at startup can corrupt production schema.

4. **Rate limit not sufficient for OTP abuse**
   - Current rate limiting is generic per-IP. OTP endpoints also need per-phone/per-tenant throttles and lockouts, with consistent `Retry-After`.

## What To Keep (v1 Strengths)

- OTP challenge model and HMAC-based OTP digest approach (with improvements).
- Service layer pattern exists (good starting point for domain services).
- Jinja2 templates already optimized for mobile/touch; several UI components can be reused.

## v2 Target Architecture (High-Level)

Mandatory structure:

```text
app/
  core/
  shared/
  domains/
    auth/
    users/
    suppliers/
    bookings/
    reviews/
    payments/
    admin/
    notifications/
  infrastructure/
main.py
```

Key architectural commitments:
- Policies: centralized authorization (`policies.py`) called from services (not routes).
- State machines: `state_machine.py` per domain where lifecycle exists; transitions produce immutable event rows.
- Repositories: explicit data access layer per domain; no raw SQL scattered across app startup.
- Migrations: Alembic-driven, deterministic, and reviewed; no schema mutation in runtime code.
- Tenant scoping: `tenant_id` required on “major tables” and enforced in repositories and policies.

