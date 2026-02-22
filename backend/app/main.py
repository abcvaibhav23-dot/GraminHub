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
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text

from app.api import admin, auth, bookings, suppliers, users
from app.core.config import Base, engine, settings, SessionLocal
from app.core.exceptions import ServiceError
from app.core.logging_config import setup_logging
from app.core.request_context import set_request_id
from app.services.supplier_service import seed_default_categories, sync_supplier_id_sequence
from app import models  # noqa: F401 - ensures model metadata is imported


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


APP_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


@app.on_event("startup")
def on_startup() -> None:
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

    db = SessionLocal()
    try:
        seed_default_categories(db)
        sync_supplier_id_sequence(db)
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
    return templates.TemplateResponse("home.html", {"request": request, "year": datetime.utcnow().year})


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


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


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(suppliers.router)
app.include_router(bookings.router)
app.include_router(admin.router)
