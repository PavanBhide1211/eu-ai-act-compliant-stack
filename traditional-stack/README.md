# Traditional baseline

The "just call the model" version. Same API surface as the compliant backend, none of the compliance controls. Used by the frontend to render the comparison side-by-side. **Do not deploy this for a real high-risk AI use case.**

Run: `docker compose up traditional` or `uvicorn app:app --port 8001`.
