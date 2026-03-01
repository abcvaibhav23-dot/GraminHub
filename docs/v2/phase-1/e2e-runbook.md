# E2E Runbook (v1 + v2)

This repo includes two E2E scripts:
- v1: `GraminHub/scripts/e2e.sh`
- v2: `GraminHub/scripts/e2e_v2.sh`

## Prerequisites

- Docker Desktop / Docker daemon running
- Backend reachable at `http://localhost:8000`
- Demo OTP exposure enabled for local E2E:
  - `OTP_EXPOSE_IN_RESPONSE=1`
  - Do **not** use this setting in production.

## Local (Docker) — recommended

From repo root:

```bash
cd GraminHub
docker compose up -d db backend
curl -fsS http://localhost:8000/health
make demo-ready
make e2e
make e2e-v2
```

## Notes for Production

- Set `APP_ENV=production`
- Set `DB_BOOTSTRAP_MODE=migrations`
- Apply migrations before starting the app:
  - `alembic upgrade head`
- Ensure `OTP_EXPOSE_IN_RESPONSE=0`

