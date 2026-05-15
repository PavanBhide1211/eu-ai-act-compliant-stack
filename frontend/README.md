# Frontend

React + Vite UI rendering the compliant backend and the traditional baseline side by side. The `ComplianceSidecar` is the differentiating component — it surfaces the Article 12 audit log, the Article 13 model card, the Article 14 oversight controls, and the Article 15/72 bias monitor live, next to the decision.

## Run

Inside docker-compose: `docker compose up frontend`. Then open http://localhost:5173.

Locally:
```
npm install
npm run dev
```

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `VITE_COMPLIANT_API` | `http://localhost:8000` | Compliant backend URL |
| `VITE_TRADITIONAL_API` | `http://localhost:8001` | Traditional baseline URL |
