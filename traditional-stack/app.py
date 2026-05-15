"""Traditional CV-screening baseline.

Deliberately minimal. Same request/response shape as the compliant backend so
the frontend can A/B them, but:

- No intended-purpose check.
- No input pseudonymisation; whatever comes in is whatever goes to the model.
- No audit log.
- No model card.
- No bias monitoring.
- No human-oversight controls (the recommendation is the answer).
- No technical documentation pack.

This is what most teams ship today. The point of putting it next to the
compliant backend is so the gap is visible at a glance.
"""

import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Traditional CV Screening API (baseline)", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CV(BaseModel):
    skills: list[str] = []
    years_experience: int = 0
    locale: str = "en"
    role_family: str | None = None
    # Note: no pseudonymisation; raw fields would pass through here.
    full_name: str | None = None
    email: str | None = None


class Job(BaseModel):
    title: str
    required_skills: list[str] = []
    min_years_experience: int = 0
    locale: str = "en"


class ScoreRequest(BaseModel):
    cv: CV
    job: Job


@app.get("/")
def root() -> dict:
    return {"name": "Traditional baseline", "stack": "traditional", "version": "0.1.0"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/screening/score")
def score(req: ScoreRequest) -> dict:
    # The exact same scoring math the compliant stub uses, but with NONE of the
    # surrounding controls.
    cv_skills = {s.lower() for s in req.cv.skills}
    job_required = {s.lower() for s in req.job.required_skills}
    if job_required:
        jaccard = len(cv_skills & job_required) / len(cv_skills | job_required)
    else:
        jaccard = 0.0
    target = req.job.min_years_experience or 0
    years = req.cv.years_experience or 0
    if target == 0 or years >= target:
        exp_factor = 1.0
    else:
        exp_factor = max(0.4, years / target)
    score_v = round(0.7 * jaccard + 0.3 * exp_factor, 4)
    rec = "shortlist" if score_v >= 0.75 else "borderline" if score_v >= 0.5 else "reject"
    return {
        "request_id": uuid.uuid4().hex,
        "recommendation": rec,
        "score": score_v,
        # No confidence, no explanation, no compliance envelope, no oversight
        # status. The traditional API returns just the answer.
    }
