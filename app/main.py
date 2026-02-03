import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.db import Base, SessionLocal, engine
from app.infrastructure.seed import seed_sample_data
from app.presentation.api import router
from app.settings import settings


def configure_logging() -> None:
    log_path = Path(settings.app_log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_level = getattr(logging, settings.log_level.upper(), logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")

    root = logging.getLogger()
    root.setLevel(log_level)

    if not any(isinstance(handler, RotatingFileHandler) and Path(getattr(handler, "baseFilename", "")) == log_path for handler in root.handlers):
        file_handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    if not any(isinstance(handler, logging.StreamHandler) for handler in root.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)

    for logger_name in ("uvicorn.error", "uvicorn.access", "app"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)


configure_logging()
logger = logging.getLogger("app")

app = FastAPI(title="Budget Management")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.middleware("http")
async def log_requests(request, call_next):
    start = perf_counter()
    logger.debug("request start %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request error %s %s", request.method, request.url.path)
        raise
    duration_ms = (perf_counter() - start) * 1000
    logger.debug(
        "request end %s %s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.on_event("startup")
def seed_on_startup():
    if settings.app_env != "dev":
        return
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_sample_data(session)


@app.get("/health")
def health_check():
    return {"status": "ok"}
