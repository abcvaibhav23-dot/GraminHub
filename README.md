# GraminHub

Rural supplier marketplace MVP built with FastAPI, PostgreSQL, Jinja2, and Tailwind.

## 1) What This Repository Contains

- Role-based platform: `guest`, `user`, `supplier`, `admin`
- Supplier discovery, call logging, WhatsApp booking, review/rating
- Admin controls: approve, block/unblock, delete supplier/user, categories, booking visibility
- Supplier controls: create/edit profiles, add/edit services, booking list
- In-page authenticated profile editor (navbar `Profile` button modal)
- Docker-first local setup (`db`, `backend`, optional `pgadmin`)
- Seeded demo data and repeatable E2E script

## 2) Tech Stack

- Backend API: FastAPI
- ORM: SQLAlchemy
- DB: PostgreSQL (Docker)
- Auth: JWT bearer token
- Templates/UI: Jinja2 + TailwindCSS + vanilla JS
- Testing: pytest + API E2E shell script
- Runtime: Docker Compose

## 3) Architecture At A Glance

- `api/`: HTTP routes and request/response glue
- `services/`: business logic and DB workflows
- `models/`: SQLAlchemy entities and relationships
- `schemas/`: request/response contracts
- `core/`: config, security, logging, request context, exceptions
- `templates/` + `static/`: server-rendered UI and browser-side logic

## 4) Project Structure

```text
GraminHub/
  backend/
    app/
      api/
      core/
      models/
      schemas/
      services/
      static/
      templates/
      tests/
    Dockerfile
    requirements.txt
    .env.example
  scripts/
    e2e.sh
    seed_demo.sql
  docker-compose.yml
  Makefile
  README.md
```

## 5) Important Repo Hygiene

- Target tracked source file budget: `<= 75` files (`git ls-files` count)
- Local generated/runtime files must not be committed (`backend/venv`, `.env`, logs, cache, backups)

Useful commands:

```bash
make clean
make clean-generated
make count-files
```

## 6) Environment Configuration

Copy and edit:

```bash
cp backend/.env.example backend/.env
```

Main variables:

| Variable | Purpose | Example |
|---|---|---|
| `APP_NAME` | Application name | `GraminHub` |
| `APP_ENV` | Environment | `development` / `production` |
| `DEBUG` | Debug mode | `0` |
| `DATABASE_URL` | SQLAlchemy connection URL | `postgresql+psycopg2://...` |
| `JWT_SECRET_KEY` | JWT signing key | long random string |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | token expiry | `60` |
| `OTP_EXPOSE_IN_RESPONSE` | expose demo OTP in API response (`1` dev, `0` prod) | `1` |
| `CORS_ORIGINS` | allowed origins | `http://localhost:8000,https://graminhub.in,https://www.graminhub.in` |
| `RATE_LIMIT_PER_MINUTE` | per-IP limit | `120` |
| `ADMIN_PHONE_ALLOWLIST` | phones allowed for Admin OTP login | `9000000001,6362272078` |

## 7) Setup And Run

### Option A: Full Docker (recommended)

```bash
docker compose up --build
```

Endpoints:

- App: `http://localhost:8000`
- Health: `http://localhost:8000/health`
- DB: `localhost:5432`
- pgAdmin: `http://localhost:5050` (optional service)

### Option B: Local backend + Docker DB

```bash
docker compose up -d db pgadmin
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## 8) Setup And Command Playbook

### First-time setup

```bash
cd /path/to/GraminHub
docker compose up -d db backend
make demo-ready
curl -fsS http://localhost:8000/health
```

### Daily startup

```bash
cd /path/to/GraminHub
docker compose up -d db backend
curl -fsS http://localhost:8000/health
```

### Quick validation

```bash
make e2e
```

### Full pre-merge validation

```bash
make demo-ready
./scripts/e2e.sh
docker compose exec -T backend sh -lc 'cd /app && PYTHONPATH=/app pytest -q app/tests'
make sanity
```

### Data utility commands

```bash
make db-reset
make db-seed-demo
make demo-ready
make db-backup
```

## 9) Demo Data

Seed command:

```bash
make db-seed-demo
```

Demo credentials:

- Admin (Owner): phone `9000000001` (OTP login, allowlisted)
- Buyer/User: phone `9000000002` (OTP login)
- Supplier 1: phone `9000000003` (OTP login)
- Supplier 2: phone `9000000004` (OTP login)
- Guest: no login required

Important behavior:

- `make db-reset` wipes users/suppliers/bookings/reviews/calls and re-inserts default categories
- After `db-reset`, run `make db-seed-demo` before login testing

## 10) UI Navigation

Public pages:

- `/`
- `/login`
- `/register`

Role pages:

- `/supplier-dashboard`
- `/admin-dashboard`

Tabbed page-inside-page structure:

- Home (`/`): `Discover & Book`, `Workflow`, `Support` tabs
- Supplier dashboard: `Setup`, `Manage Records`, `Bookings` tabs
- Supplier manage tab includes nested tabs: `Supplier Profiles`, `Supplier Services`
- Admin dashboard: `Supplier Ops`, `Configuration`, `Data & Moderation` tabs
- Admin data tab includes nested tabs: `Pending Suppliers`, `All Bookings`, `Delete IDs`

Search options on Home:

- Global top search bar (Home page): keyword/sentence/voice search.
- Quick-tag search is placed at the top (next to global search) for village-friendly fast discovery.
- Old duplicate in-page search blocks were removed from Home content to keep one clear search flow.
- Home page keeps disclaimer section at the end of the page with full details on `/privacy`.

Profile editing:

- Click navbar `Profile` after login
- Opens in-page profile panel modal (not a separate workflow page)

Language switch note:

- Hindi/English switch now updates app text via `data-ui-lang` and avoids browser language popups caused by changing document `lang` dynamically.

## 11) API Surface (By Role)

### Public/Guest/User

- `GET /api/suppliers/categories`
- `GET /api/suppliers/search`
- `GET /api/suppliers/{id}`
- `POST /api/bookings`
- `POST /api/bookings/whatsapp`
- `POST /api/bookings/guest`
- `POST /api/bookings/guest/whatsapp`
- `POST /api/suppliers/{id}/reviews`
- `GET /api/users/me`
- `PUT /api/users/me`
- `POST /api/users/me/update` (legacy fallback route)

### Supplier (admin can also use these supplier edit endpoints)

- `POST /api/suppliers/profile`
- `GET /api/suppliers/me/profiles`
- `PUT /api/suppliers/profiles/{id}`
- `POST /api/suppliers/services`
- `GET /api/suppliers/me/services`
- `PUT /api/suppliers/services/{id}`
- `GET /api/suppliers/me/bookings`

### Admin

- `GET /api/admin/pending-suppliers`
- `POST /api/admin/suppliers/{id}/approve`
- `POST /api/admin/suppliers/{id}/block`
- `POST /api/admin/suppliers/{id}/unblock`
- `DELETE /api/admin/suppliers/{id}`
- `DELETE /api/admin/users/{id}`
- `POST /api/admin/categories`
- `GET /api/admin/bookings`

### Ops

- `GET /health`

## 12) Test Checklist

### Guest

- Language switch Hindi/English
- Supplier search and card rendering
- Guest WhatsApp booking
- Guest direct call

### User

- Login
- Navbar Profile modal edit
- Search + booking + WhatsApp booking
- Review/rating flow

### Supplier

- Login
- Create new supplier profile (new supplier ID)
- Add service
- Load/edit profiles by ID
- Load/edit services by ID
- Check supplier bookings

### Admin

- Login
- Approve supplier ID from pending list
- Block/unblock supplier
- Delete supplier/user by ID
- Category create
- View all bookings

## 13) Validation Commands

```bash
# compile + optional tests + e2e-if-running + file-budget
make sanity

# unit/API tests (inside backend venv or container)
cd backend
pytest app/tests -q

# live API e2e
make e2e
```

## 14) Deployment Checklist

1. Set production `JWT_SECRET_KEY`
2. Keep `DEBUG=0`
3. Set strict `CORS_ORIGINS` for production domains
4. Use managed PostgreSQL in production
5. Run sanity and tests before release
6. Confirm only intended files in `git status --short`

Example production CORS:

```bash
CORS_ORIGINS=https://graminhub.in,https://www.graminhub.in
```

### Vercel Deployment Notes

- This repo deploys via `vercel.json` with ASGI entrypoint `api/index.py`.
- All routes are rewritten to FastAPI app, so `/`, `/login`, `/admin-dashboard`, APIs, and static assets resolve through the same backend function.
- Root `requirements.txt` points to `backend/requirements.txt` for Vercel dependency install.
- Root `pyproject.toml` is included with a valid `[project]` table so Vercel/uv install step does not fail.
- Python runtime is resolved from `pyproject.toml` (`requires-python = ">=3.12"`).
- `vercel.json` intentionally avoids legacy `builds` and explicit function runtime blocks.
- SEO support includes `robots.txt`, `sitemap.xml`, Open Graph tags, and a generated keyword corpus (`backend/app/core/seo_keywords.py`).
- Privacy note page is available at `/privacy` (also `/privacy-policy`).
- If `DATABASE_URL` is not set, app falls back to sqlite on `/tmp/graminhub.db` (non-persistent, demo-only).

Recommended Vercel environment variables:

- `DATABASE_URL` (production managed Postgres)
- `JWT_SECRET_KEY` (strong secret)
- `APP_ENV=production`
- `DEBUG=0`
- `CORS_ORIGINS=https://graminhub.in,https://www.graminhub.in`

Support contact:

- Email: `cba.vaibhav23@gmail.com`
- Phone/WhatsApp: `+91-6362272078`

## 15) Troubleshooting

- Login returns `401`: demo seed missing, run `make db-seed-demo`
- Supplier not visible on home: supplier must be approved and have matching category/service
- Supplier ID mismatch confusion: use IDs from `Pending Suppliers` output
- Duplicate/reused supplier ID issue: restart backend and run `make demo-ready` once
- Profile save shows not found: restart backend with latest routes and JS
- Too many changed files: run `make clean-generated`

## 16) HLD (High-Level Design)

### 16.1 Context

GraminHub is a server-rendered marketplace where end users discover and book suppliers, suppliers manage offerings, and admins control trust/operations.

### 16.2 Major Components

- Web UI Layer: Jinja2 templates + Tailwind + JS (`static/js/app.js`)
- API Layer: FastAPI routers (`app/api/*`)
- Domain Layer: Service modules (`app/services/*`)
- Persistence Layer: SQLAlchemy models + PostgreSQL (`app/models/*`)
- Cross-cutting: Auth/JWT, logging, request ID, rate limit (`app/core/*`)

### 16.3 Data Stores

Primary DB tables:

- `users`
- `suppliers`
- `supplier_services`
- `bookings`
- `reviews`
- `call_logs`
- `categories`

### 16.4 Security Model

- JWT bearer auth
- Role checks (`user`, `supplier`, `admin`)
- API-level authorization + UI guard/redirect logic

## 17) LLD (Low-Level Design)

### 17.1 Request Lifecycle

1. Browser action triggers JS function in `app.js`
2. JS calls route via `fetch`
3. FastAPI route validates payload with Pydantic schema
4. Route delegates to service layer
5. Service executes DB operations using SQLAlchemy session
6. Route returns normalized response
7. UI renders response payload in relevant panel

### 17.2 Key Backend Modules

- `app/api/auth.py`: register + phone OTP token issuance
- `app/api/users.py`: own-profile read/update
- `app/api/suppliers.py`: search, profile/service create/edit, bookings/reviews
- `app/api/admin.py`: approval, moderation, delete operations, categories
- `app/services/supplier_service.py`: supplier/profile/service business rules and ID sequence handling
- `app/services/booking_service.py`: booking and WhatsApp URL composition
- `app/services/review_service.py`: rating/review upsert and summaries
- `app/services/call_service.py`: call logging

### 17.3 Frontend Module Responsibilities

- `static/js/app.js`:
  - auth token handling
  - role-aware navbar and access control
  - language switch mapping and UI text dictionary
  - supplier search render
  - booking/call/rating actions
  - admin operations
  - in-page profile modal flows

### 17.4 Error Handling

- Service-layer typed exceptions (`NotFoundError`, `ConflictError`, etc.)
- Global exception handlers in `main.py`
- UI shows response payload in panel outputs

## 18) Flow-Wise Tech Mapping

### 18.1 Authentication Flow

- Frontend: `app.js` login/register handlers
- API: `POST /api/auth/register`, `POST /api/auth/otp/request`, `POST /api/auth/otp/verify`
- Guardrails: public admin registration is blocked; admin OTP is allowed only for `ADMIN_PHONE_ALLOWLIST`
- Security: JWT encode/decode (`core/security.py`)
- Storage: `users` table

### 18.2 Supplier Discovery Flow

- Frontend: `searchSuppliers()`, `renderSuppliers()`
- API: `GET /api/suppliers/search`, `GET /api/suppliers/categories`
- Service: `search_suppliers()`
- Storage: `suppliers`, `supplier_services`, `categories`, `reviews`

### 18.3 Booking + WhatsApp Flow

- Frontend: `bookViaWhatsApp()`
- API: booking endpoints (`/api/bookings*`)
- Service: `booking_service.py`
- External integration: WhatsApp deep-link URL
- Storage: `bookings`

### 18.4 Supplier Profile/Service Management Flow

- Frontend: supplier dashboard create/edit forms with item name/details/variant + optional 3 photo URLs
- API: `/api/suppliers/profile`, `/api/suppliers/profiles/{id}`, `/api/suppliers/services`, `/api/suppliers/services/{id}`
- Service: `supplier_service.py`
- Storage: `suppliers`, `supplier_services`

### 18.5 Admin Moderation Flow

- Frontend: admin dashboard actions
- API: `/api/admin/suppliers/{id}/approve|block|unblock|delete`, `/api/admin/users/{id}`
- Service/Route logic: `api/admin.py` + SQLAlchemy model cascades
- Storage: `suppliers`, `users`, related child data by FK cascade

### 18.6 Profile Edit Flow (All Roles)

- Frontend: navbar `Profile` modal in `base.html` + `app.js`
- API: `PUT /api/users/me` (fallback `POST /api/users/me/update`)
- Service: `update_user_profile()`
- Storage: `users`

### 18.7 Ratings And Calls Flow

- Frontend: `rateSupplier()`, `callSupplier()`
- API: `/api/suppliers/{id}/reviews`, `/api/suppliers/{id}/call`
- Service: `review_service.py`, `call_service.py`
- Storage: `reviews`, `call_logs`

## 19) Final Pre-Commit Checklist

```bash
make clean
make count-files
make sanity
git status --short
```

Commit only intended source/config/docs changes.
