"""Provider-agnostic model wrapper.

Defaults to a deterministic stub so the demo runs without any API keys. Switch
to a real provider by setting LITELLM_PROVIDER and the appropriate API-key env
var (OPENAI_API_KEY / ANTHROPIC_API_KEY / OLLAMA_HOST).
"""

import hashlib
import json
from typing import Optional

from app.config import settings


class LLMClient:
    def __init__(self) -> None:
        self.provider = settings.litellm_provider
        self.model = settings.litellm_model

    def score_cv(self, *, cv: dict, job: dict) -> dict:
        """Return a typed scoring object: score, confidence, explanation."""
        if self.provider == "stub":
            return self._stub_score(cv, job)
        return self._litellm_score(cv, job)

    # ------------------------------------------------------------ stub
    def _stub_score(self, cv: dict, job: dict) -> dict:
        """Deterministic, explainable scoring used in the demo.

        Score is computed as the Jaccard similarity between the CV skill set
        and the job required-skill set, plus an experience match bonus. This
        is intentionally simple and transparent: it lets reviewers see exactly
        why a candidate scored where they did, which is the point of the
        compliant pattern.
        """
        cv_skills = {s.lower() for s in cv.get("skills", [])}
        job_required = {s.lower() for s in job.get("required_skills", [])}
        if not job_required:
            jaccard = 0.0
        else:
            inter = cv_skills & job_required
            union = cv_skills | job_required
            jaccard = len(inter) / len(union) if union else 0.0

        years = cv.get("years_experience", 0) or 0
        target = job.get("min_years_experience", 0) or 0
        if target == 0:
            exp_factor = 1.0
        elif years >= target:
            exp_factor = 1.0
        else:
            exp_factor = max(0.4, years / target)

        score = round(0.7 * jaccard + 0.3 * exp_factor, 4)
        # Confidence: stub is deterministic so we report a fixed mid value to
        # remind the reviewer that confidence here is a property of the model,
        # not of the answer.
        confidence = 0.65

        matched = sorted(cv_skills & job_required)
        missing = sorted(job_required - cv_skills)
        explanation_parts = []
        if matched:
            explanation_parts.append(
                f"Matched required skills: {', '.join(matched)}."
            )
        if missing:
            explanation_parts.append(
                f"Missing required skills: {', '.join(missing)}."
            )
        explanation_parts.append(
            f"Years of experience: {years} (role target {target})."
        )
        explanation_parts.append(
            "This recommendation is advisory. A competent recruiter must "
            "review before any decision is communicated to the candidate."
        )
        return {
            "score": score,
            "confidence": confidence,
            "explanation": " ".join(explanation_parts),
            "model_version": f"{self.model}",
        }

    # ------------------------------------------------------------ litellm
    def _litellm_score(self, cv: dict, job: dict) -> dict:
        """Call a real provider via LiteLLM. Output is constrained to a typed
        schema; deviations are rejected and we fall back to the stub.
        """
        try:
            from litellm import completion  # type: ignore
        except Exception:
            return self._stub_score(cv, job)

        prompt = self._build_prompt(cv, job)
        try:
            resp = completion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a structured CV-scoring assistant. "
                            "Return strictly JSON with keys score (0..1), "
                            "confidence (0..1), explanation (string). "
                            "Do not infer protected attributes. Refuse to "
                            "include the candidate's name, address, photo, "
                            "or any sensitive attribute in the explanation."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            text = resp["choices"][0]["message"]["content"]  # type: ignore
            data = json.loads(text)
            return {
                "score": float(data["score"]),
                "confidence": float(data.get("confidence", 0.5)),
                "explanation": str(data["explanation"]),
                "model_version": self.model,
            }
        except Exception:
            # Fail-safe: never return an unstructured output from the model.
            return self._stub_score(cv, job)

    def _build_prompt(self, cv: dict, job: dict) -> str:
        return (
            "Score this candidate against this job description. Do not infer "
            "protected attributes. Output JSON only.\n\n"
            f"JOB:\n{json.dumps(job, sort_keys=True)}\n\n"
            f"CANDIDATE:\n{json.dumps(cv, sort_keys=True)}\n"
        )


def fingerprint(obj: dict | str, *, salt: str = "demo-salt") -> str:
    """Salted SHA-256 fingerprint for PII-bearing inputs."""
    raw = obj if isinstance(obj, str) else json.dumps(obj, sort_keys=True)
    return hashlib.sha256((salt + raw).encode("utf-8")).hexdigest()[:32]


def recommendation_for_score(score: float) -> str:
    if score >= 0.75:
        return "shortlist"
    if score >= 0.5:
        return "borderline"
    return "reject"
