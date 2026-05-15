"""Structured CV / job-description normalisation.

The compliant pattern is to NEVER pass raw free-form text to the model. We
extract a typed view first, both to defend against prompt injection and to make
the model's input auditable.
"""

from pydantic import BaseModel, Field


class CV(BaseModel):
    skills: list[str] = Field(default_factory=list)
    years_experience: int = 0
    locale: str = "en"
    role_family: str | None = None
    # Optional self-reported, pseudonymisable bucket — used only for bias
    # monitoring under Article 10(5) safeguards.
    self_reported_cohort: str | None = None


class JobDescription(BaseModel):
    title: str
    required_skills: list[str] = Field(default_factory=list)
    min_years_experience: int = 0
    locale: str = "en"
    role_family: str | None = None


class ScreeningRequest(BaseModel):
    cv: CV
    job: JobDescription
    deployer_id: str
    requested_by_user: str | None = None


def derive_bias_cohort(cv: CV) -> str:
    """Pseudonymise the bias-monitoring bucket. Locale + experience band is a
    sufficient first-pass cohort; richer cohorts can be added once the deployer
    has done its FRIA and identified the relevant subgroups."""
    if cv.years_experience < 2:
        band = "band_junior"
    elif cv.years_experience < 7:
        band = "band_mid"
    else:
        band = "band_senior"
    return f"{cv.locale}_{band}"
