FROM python:3.11-slim

WORKDIR /app

# Build context is the repo root, so paths below are relative to it.
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY i18n/ /app/i18n/

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV COMPLIANCE_DB_PATH=/app/data/compliance.db

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
