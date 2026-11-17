FROM python:3.11-slim AS builder

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir pip setuptools wheel && \
    pip install --no-cache-dir -e .

FROM python:3.11-slim AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

WORKDIR /app

COPY --from=builder /app/.python-packages /app/.python-packages
COPY --from=builder /app/src ./src
COPY --from=builder /app/pyproject.toml ./
COPY --from=builder /app/poetry.lock* ./

RUN pip install --no-cache-dir -r pyproject.toml

COPY backend/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "$APP_HOST", "--port", "$APP_PORT"]