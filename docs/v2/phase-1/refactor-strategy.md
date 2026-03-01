# GraminHub v1 → v2 (Phase 1) — Refactoring Strategy (Clean Architecture)

Date: 2026-02-28

Goal: deliver a production-grade, SaaS-ready v2 with clean domain separation, strict policies, explicit state machines, tenant isolation, and full testing—without relying on v1 assumptions.

## Guiding Principles

- Separate concerns by domain; no “shared service soup”.
- No permission logic in routes; routes only translate HTTP ↔ use-cases.
- Policies are centralized and unit tested.
- State machines are explicit and unit tested; every transition produces an event.
- Repositories enforce tenant scoping.
- Migrations are the only way the schema changes (no startup DDL).

## Recommended Cutover Plan (Incremental, Low-Risk)

### Step 1 — Create v2 skeleton alongside v1
- Add v2 package with the mandated directory structure.
- Wire a v2 router prefix (e.g., `/v2/*`) to allow incremental rollout without breaking v1.

### Step 2 — Build shared infrastructure primitives
- `core/`: config, logging, auth dependencies, error handling, request context.
- `shared/`: time utils, ids, pagination, base repository helpers, tenancy context.
- `infrastructure/`: DB session, migrations, OTP provider adapters, notification providers.

### Step 3 — Implement domains in dependency order
1. `auth/` + `users/`
2. `suppliers/` (verification lifecycle + documents)
3. `bookings/` (state machine + events)
4. `reviews/`
5. `payments/` + commissions
6. `admin/` (ops & moderation)
7. `notifications/`

### Step 4 — Replace v1 UI with rural-first v2 UI
- Keep old endpoints with redirects; avoid breaking deep links.
- Use fewer screens and route-per-task pages.

### Step 5 — Decommission v1 code paths
- Remove v1 startup DDL.
- Drop v1 routers once v2 covers parity.

## Testing Strategy (Build Confidence Early)

- Unit tests:
  - Policy engine (positive + negative + privilege escalation attempts).
  - Booking transitions (legal + illegal).
  - Supplier lifecycle transitions.
  - OTP throttling behavior.
- Integration tests:
  - API flows: login → create booking → supplier accept → complete.
  - Tenant isolation.
- UI smoke tests:
  - Critical rural flow pages render; basic interactions work.

## Deliverables Produced In Phase 1

- Architecture audit
- UX simplification report
- Breaking risks list
- This refactor strategy

