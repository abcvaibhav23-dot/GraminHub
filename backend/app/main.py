"""FastAPI app entrypoint."""
from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text

from app.api import admin, auth, bookings, public, suppliers, users
from app.core.config import Base, engine, settings, SessionLocal
from app.core.exceptions import ServiceError
from app.core.logging_config import setup_logging
from app.core.request_context import set_request_id
from app.core.seo_keywords import SEO_KEYWORDS, SEO_META_KEYWORDS
from app.services.supplier_service import seed_default_categories, sync_supplier_id_sequence
from app.services.site_setting_service import seed_site_settings
from app import models  # noqa: F401 - ensures model metadata is imported
from app.domains.bookings.router import router as v2_bookings_router
from app.domains.suppliers.router import router as v2_suppliers_router
from app.shared.ai.router import router as v2_ai_router


setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
if not origins:
    origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rate_buckets: dict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    now = time.time()
    ip = request.client.host if request.client else "unknown"
    bucket = rate_buckets[ip]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= settings.RATE_LIMIT_PER_MINUTE:
        logger.warning("Rate limit exceeded ip=%s path=%s", ip, request.url.path)
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    bucket.append(now)
    return await call_next(request)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    set_request_id(request_id)
    request.state.request_id = request_id

    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        latency_ms = (time.perf_counter() - started) * 1000
        logger.exception(
            "Request failed method=%s path=%s latency_ms=%.2f",
            request.method,
            request.url.path,
            latency_ms,
        )
        raise

    latency_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "Request completed method=%s path=%s status=%s latency_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        latency_ms,
    )
    return response


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    # Allow microphone for rural-friendly voice search. Keep camera/geolocation disabled by default.
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(self), camera=()")
    if settings.APP_ENV.lower() == "production":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


APP_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")
templates.env.globals["seo_keywords_cloud"] = SEO_KEYWORDS
templates.env.globals["seo_keywords_meta"] = SEO_META_KEYWORDS
templates.env.globals["public_support_email"] = settings.PUBLIC_SUPPORT_EMAIL
templates.env.globals["public_support_phone"] = settings.PUBLIC_SUPPORT_PHONE
templates.env.globals["public_support_whatsapp"] = settings.PUBLIC_SUPPORT_WHATSAPP
templates.env.globals["app_env"] = settings.APP_ENV
templates.env.globals["ui_mode"] = settings.UI_MODE
templates.env.globals["show_demo_hints"] = settings.SHOW_DEMO_HINTS
templates.env.globals["ai_search_enabled"] = settings.AI_SEARCH_ENABLED


@app.on_event("startup")
def on_startup() -> None:
    if settings.DB_BOOTSTRAP_MODE == "migrations":
        logger.info("DB bootstrap mode is migrations; skipping runtime schema changes and seeding")
        return

    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)

    if engine.dialect.name == "postgresql":
        unique_constraints = inspector.get_unique_constraints("suppliers")
        for constraint in unique_constraints:
            columns = constraint.get("column_names") or []
            constraint_name = constraint.get("name")
            if columns == ["user_id"] and constraint_name:
                with engine.begin() as conn:
                    conn.execute(text(f'ALTER TABLE suppliers DROP CONSTRAINT IF EXISTS "{constraint_name}"'))
                logger.info("Schema updated: removed unique constraint on suppliers.user_id")
                break

    supplier_columns = {col["name"] for col in inspector.get_columns("suppliers")}
    if "blocked" not in supplier_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE suppliers ADD COLUMN blocked BOOLEAN NOT NULL DEFAULT FALSE"))
        logger.info("Schema updated: added suppliers.blocked column")

    booking_columns = {col["name"] for col in inspector.get_columns("bookings")}
    if "guest_name" not in booking_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE bookings ADD COLUMN guest_name VARCHAR(120)"))
        logger.info("Schema updated: added bookings.guest_name column")
    if "guest_phone" not in booking_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE bookings ADD COLUMN guest_phone VARCHAR(30)"))
        logger.info("Schema updated: added bookings.guest_phone column")

    user_columns = {col["name"] for col in inspector.get_columns("users")}
    if "phone" not in user_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(30)"))
        logger.info("Schema updated: added users.phone column")
    if "blocked" not in user_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN blocked BOOLEAN NOT NULL DEFAULT FALSE"))
        logger.info("Schema updated: added users.blocked column")

    site_setting_columns = {col["name"] for col in inspector.get_columns("site_settings")}
    if "str_value" not in site_setting_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE site_settings ADD COLUMN str_value VARCHAR(500)"))
        logger.info("Schema updated: added site_settings.str_value column")

    supplier_service_columns = {col["name"] for col in inspector.get_columns("supplier_services")}
    if "item_name" not in supplier_service_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE supplier_services ADD COLUMN item_name VARCHAR(160)"))
        logger.info("Schema updated: added supplier_services.item_name column")
    if "item_details" not in supplier_service_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE supplier_services ADD COLUMN item_details VARCHAR(500)"))
        logger.info("Schema updated: added supplier_services.item_details column")
    if "item_variant" not in supplier_service_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE supplier_services ADD COLUMN item_variant VARCHAR(160)"))
        logger.info("Schema updated: added supplier_services.item_variant column")
    if "photo_url_1" not in supplier_service_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE supplier_services ADD COLUMN photo_url_1 VARCHAR(500)"))
        logger.info("Schema updated: added supplier_services.photo_url_1 column")
    if "photo_url_2" not in supplier_service_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE supplier_services ADD COLUMN photo_url_2 VARCHAR(500)"))
        logger.info("Schema updated: added supplier_services.photo_url_2 column")
    if "photo_url_3" not in supplier_service_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE supplier_services ADD COLUMN photo_url_3 VARCHAR(500)"))
        logger.info("Schema updated: added supplier_services.photo_url_3 column")
    if "price_unit_type" not in supplier_service_columns:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE supplier_services ADD COLUMN price_unit_type VARCHAR(40) NOT NULL DEFAULT 'per_item'"
                )
            )
        logger.info("Schema updated: added supplier_services.price_unit_type column")

    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE supplier_services ALTER COLUMN category_id DROP NOT NULL"))
            conn.execute(text("ALTER TABLE supplier_services ALTER COLUMN price DROP NOT NULL"))

    category_columns = {col["name"] for col in inspector.get_columns("categories")}
    if "key" not in category_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE categories ADD COLUMN key VARCHAR(80)"))
        logger.info("Schema updated: added categories.key column")
    if "is_enabled" not in category_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE categories ADD COLUMN is_enabled BOOLEAN NOT NULL DEFAULT TRUE"))
        logger.info("Schema updated: added categories.is_enabled column")

    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_categories_is_enabled ON categories (is_enabled)"))

    db = SessionLocal()
    try:
        # Backfill category keys/enabled flags for existing installs before seeding.
        rows = db.execute(
            text("SELECT id, name, COALESCE(key, '') AS key, COALESCE(is_enabled, TRUE) AS is_enabled FROM categories")
        ).mappings().all()
        name_to_defaults = {
            "Building Materials": ("building_material", True),
            "Vehicle Booking": ("vehicle_booking", True),
            "Agriculture Supplies": ("agriculture_supplies", False),
            "Equipment Rental": ("equipment_rental", False),
            "Local Services": ("local_services", False),
            # Backward compatibility (older names)
            "Construction Materials": ("building_material", True),
            "Heavy Vehicles": ("vehicle_booking", True),
            "Transport Vehicles": ("vehicle_booking", True),
            "Equipment Rentals": ("equipment_rental", False),
        }
        def _key_from_name(name: str) -> str:
            normalized = "".join(ch if ch.isalnum() else "_" for ch in (name or "").strip().lower())
            collapsed = "_".join(part for part in normalized.split("_") if part)
            return (collapsed[:80] or "category")

        for row in rows:
            defaults = name_to_defaults.get(row["name"])
            if defaults:
                key, enabled = defaults
            else:
                key, enabled = (_key_from_name(row["name"]), False)

            if row["key"] != key or bool(row["is_enabled"]) != bool(enabled) or not row["key"]:
                db.execute(
                    text("UPDATE categories SET key = :key, is_enabled = :enabled WHERE id = :id"),
                    {"key": key, "enabled": enabled, "id": row["id"]},
                )

        seed_default_categories(db)
        seed_site_settings(db)
        sync_supplier_id_sequence(db)
        db.commit()

        # Enforce constraints post-backfill for PostgreSQL installs.
        if db.bind is not None and db.bind.dialect.name == "postgresql":
            missing_keys = db.execute(
                text("SELECT COUNT(*) FROM categories WHERE key IS NULL OR key = ''")
            ).scalar_one()
            duplicates = db.execute(
                text("SELECT COUNT(*) FROM (SELECT key FROM categories GROUP BY key HAVING COUNT(*) > 1) t")
            ).scalar_one()
            if int(missing_keys) == 0 and int(duplicates) == 0:
                db.execute(text("ALTER TABLE categories ALTER COLUMN key SET NOT NULL"))
                db.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ux_categories_key ON categories (key)"))
                db.commit()
    finally:
        db.close()
    logger.info("Application startup completed")


@app.exception_handler(ServiceError)
async def service_exception_handler(_: Request, exc: ServiceError):
    logger.info("Service exception status=%s detail=%s", exc.status_code, exc.message)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception):
    logger.error("Unhandled error: %s", str(exc), exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
def home(request: Request):
    template_name = "v2/home.html" if settings.UI_MODE == "v2" else "home.html"
    return templates.TemplateResponse(template_name, {"request": request, "year": datetime.utcnow().year})


@app.get("/v2")
def home_v2(request: Request):
    return templates.TemplateResponse("v2/home.html", {"request": request, "year": datetime.utcnow().year})


@app.get("/login")
def login_page(request: Request):
    template_name = "v2/login.html" if settings.UI_MODE == "v2" else "login.html"
    return templates.TemplateResponse(template_name, {"request": request})


@app.get("/v2/login")
def login_page_v2(request: Request):
    return templates.TemplateResponse("v2/login.html", {"request": request})


@app.get("/register")
def register_page(request: Request):
    template_name = "v2/register.html" if settings.UI_MODE == "v2" else "register.html"
    return templates.TemplateResponse(template_name, {"request": request})


@app.get("/v2/register")
def register_page_v2(request: Request):
    return templates.TemplateResponse("v2/register.html", {"request": request})


@app.get("/privacy")
@app.get("/privacy-policy")
def privacy_page(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})


@app.get("/profile")
@app.get("/profile/")
@app.get("/account")
@app.get("/account/")
def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/supplier-dashboard")
def supplier_dashboard(request: Request):
    return templates.TemplateResponse("supplier_dashboard.html", {"request": request})


@app.get("/admin-dashboard")
def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "utc": datetime.utcnow().isoformat() + "Z"}


@app.get("/robots.txt", include_in_schema=False)
def robots_txt() -> PlainTextResponse:
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Sitemap: https://graminhub.in/sitemap.xml\n"
    )
    return PlainTextResponse(content=content)


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml() -> Response:
    urls = ["/", "/login", "/register", "/supplier-dashboard", "/admin-dashboard", "/privacy"]
    lastmod = datetime.utcnow().date().isoformat()
    body = "".join(
        f"<url><loc>https://graminhub.in{path}</loc><lastmod>{lastmod}</lastmod></url>"
        for path in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{body}"
        "</urlset>"
    )
    return Response(content=xml, media_type="application/xml")


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(suppliers.router)
app.include_router(bookings.router)
app.include_router(public.router)
app.include_router(admin.router)

# v2 (Clean Architecture) routers are mounted alongside v1 during migration.
app.include_router(v2_suppliers_router)
app.include_router(v2_bookings_router)
app.include_router(v2_ai_router)
