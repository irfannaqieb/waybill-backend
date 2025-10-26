# ---------- builder ----------
FROM python:3.11-slim AS builder
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
  
  RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential gcc libpq-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*
  
  RUN python -m venv /opt/venv
  ENV PATH="/opt/venv/bin:$PATH"
  
  COPY requirements.txt pyproject.toml ./
  RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
  RUN if [ -f pyproject.toml ]; then pip install . ; fi
  
  # ---------- runtime ----------
  FROM python:3.11-slim
  WORKDIR /app
  ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
  # non-root
  RUN useradd -m appuser
  # copy only the venv and app
  COPY --from=builder /opt/venv /opt/venv
  ENV PATH="/opt/venv/bin:$PATH"
  COPY . /app
  USER appuser
  
EXPOSE 8000
CMD ["gunicorn","-k","uvicorn.workers.UvicornWorker","app.main:app","--bind","0.0.0.0:8000","--workers","2","--timeout","60"]
  