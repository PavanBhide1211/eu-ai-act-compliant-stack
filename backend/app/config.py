"""Runtime configuration. Sensible defaults for demo; overridable via env."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App identity ---
    app_name: str = "EU AI Act Compliant CV Screening API"
    app_version: str = "0.2.0-day2"

    # --- Storage ---
    compliance_db_path: str = "./data/compliance.db"

    # --- Model layer ---
    # When LITELLM_PROVIDER is "stub" (default in demo), the LLM client returns
    # a deterministic, locally-computed score so the demo runs without API keys.
    # Set to "openai" / "anthropic" / "ollama" etc. with the appropriate
    # API key env var to switch to a real provider.
    litellm_provider: str = "stub"
    litellm_model: str = "stub-cv-scorer-v1"

    # --- Compliance policy knobs ---
    audit_log_retention_days: int = 365  # Article 12 retention. Six months is the
                                         # floor in the Act for some categories;
                                         # we use a year for safety.
    bias_alert_threshold: float = 0.10   # absolute delta in selection rate
                                         # between protected groups before
                                         # we raise a bias alert.
    require_two_person_oversight: bool = True   # Article 14 for biometric ID is
                                                # explicit; we mirror it for
                                                # high-impact HR decisions.

    # --- System identity (used in audit log and model card) ---
    system_id: str = "cv-screener-eu-ai-act-demo"
    system_intended_purpose_file: str = "./app/system_intended_purpose.yaml"

    # --- CORS for the React frontend ---
    cors_origins: list[str] = ["http://localhost:5173", "http://frontend:5173"]


settings = Settings()


def db_path() -> Path:
    p = Path(settings.compliance_db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p
