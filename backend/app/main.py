"""Compliant backend entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db, SessionLocal
from app.api.screening import router as screening_router
from app.api.compliance_routes import router as compliance_router
from app.api.i18n_routes import router as i18n_router
from app.compliance import risk_register, data_lineage, intended_purpose


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Validate intended purpose before doing anything else.
    intended_purpose.load_intended_purpose()
    init_db()
    with SessionLocal() as s:
        risk_register.seed_if_empty(s)
        data_lineage.seed_if_empty(s)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Compliant CV-screening reference implementation. Implements the "
        "obligations of Articles 8-15 of Regulation (EU) 2024/1689 for a "
        "high-risk AI system (Annex III, point 4(a))."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(screening_router)
app.include_router(compliance_router)
app.include_router(i18n_router)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "stack": "compliant",
        "docs": "/docs",
        "endpoints": {
            "screening": "/screening/score",
            "intended_purpose": "/compliance/intended-purpose",
            "risk_register": "/compliance/risk-register",
            "data_lineage": "/compliance/data-lineage",
            "audit_log": "/compliance/audit-log",
            "model_card": "/compliance/model-card",
            "oversight": "/compliance/oversight",
            "bias_monitor": "/compliance/bias-monitor",
            "technical_documentation": "/compliance/technical-documentation.md",
            "candidate_disclosure": "/compliance/candidate-disclosure",
            "i18n_locales": "/i18n/locales",
            "i18n_reload": "/i18n/reload",
        },
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
