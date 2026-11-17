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

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY pyproject.toml ./

RUN pip install --no-cache-dir -r pyproject.toml

COPY backend/app ./app

EXPOSE 8000

RUN apt-get update && \
    apt-get install -y --no-install-recommends runsc && \
    rm -rf /var/lib/apt/lists/*

CMD ["runsc", "run", "--port", "$APP_PORT", "--host", "$APP_HOST", "uvicorn", "app.main:app", "--host", "$APP_HOST", "--port", "$APP_PORT"]