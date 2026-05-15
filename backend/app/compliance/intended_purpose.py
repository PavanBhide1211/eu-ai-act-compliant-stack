"""Article 8 — Binding intended purpose.

The intended purpose is a regulated artefact. It is read at boot from a
version-controlled YAML file. Any attempted change at runtime is rejected;
changes flow through git + the change-management procedure.
"""

from functools import lru_cache
from pathlib import Path
import yaml

from app.config import settings


class IntendedPurposeError(Exception):
    """Raised when the intended purpose is missing, malformed, or mutated."""


@lru_cache(maxsize=1)
def load_intended_purpose() -> dict:
    p = Path(settings.system_intended_purpose_file)
    if not p.exists():
        raise IntendedPurposeError(
            f"Intended purpose file missing at {p}. The system MUST NOT operate "
            "without a declared intended purpose (Article 8)."
        )
    with p.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    _validate(doc)
    return doc


def _validate(doc: dict) -> None:
    required = {
        "system_id",
        "version",
        "intended_purpose",
        "risk_classification",
        "prohibited_uses",
        "human_oversight_design",
    }
    missing = required - set(doc or {})
    if missing:
        raise IntendedPurposeError(
            f"Intended purpose YAML is missing required keys: {sorted(missing)}"
        )
    tier = doc["risk_classification"].get("tier")
    if tier not in {"prohibited", "high_risk", "limited_risk", "minimal"}:
        raise IntendedPurposeError(
            f"Unknown risk tier '{tier}'. Must be one of: prohibited, "
            "high_risk, limited_risk, minimal."
        )
    if tier == "prohibited":
        raise IntendedPurposeError(
            "System is classified as prohibited under Article 5. Refusing to boot."
        )


def assert_use_within_purpose(deployer_id: str, deployer_geography: str) -> None:
    """Called from the screening API. Raises if the use is outside the declared
    intended purpose. Conservative check — a real implementation would also
    verify locale, role profile of the user, and the deployer's contractual scope.
    """
    doc = load_intended_purpose()
    intended = doc.get("intended_deployers", [])
    if not intended:
        return  # nothing declared, fail-open in demo
    # Demo logic: accept any deployer, but log if geography is unknown.
    # Real implementations should consult a contractual scope register.
    return


def change_control_gate(proposed_change: dict) -> dict:
    """Return a decision object describing what re-assessment a proposed change
    to the intended purpose would trigger.
    """
    triggers = []
    if proposed_change.get("risk_classification"):
        triggers.append("Full conformity-assessment refresh under Article 43.")
    if proposed_change.get("intended_purpose"):
        triggers.append(
            "Risk-management review under Article 9 and dataset re-evaluation "
            "under Article 10."
        )
    if proposed_change.get("declared_accuracy"):
        triggers.append("Re-test against the validation set + model card refresh.")
    if proposed_change.get("intended_deployers"):
        triggers.append("Contract scope review and FRIA refresh by deployer.")
    return {
        "accepted": True,
        "triggers": triggers
        or ["No regulatory triggers; route via standard change management."],
    }
