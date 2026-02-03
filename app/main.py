from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.db import Base, SessionLocal, engine
from app.infrastructure.seed import seed_sample_data
from app.presentation.api import router
from app.settings import settings

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
