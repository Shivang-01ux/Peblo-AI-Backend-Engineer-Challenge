# ────────────────────────────────────────────────────────────────
# Peblo AI Mini — Dockerfile (multi-stage)
# ────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Install system dependencies ──────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# ── Install Python dependencies ─────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Download NLTK data ──────────────────────────────────────────
RUN python -c "import nltk; nltk.download('punkt_tab', quiet=True); nltk.download('stopwords', quiet=True)"

# ── Copy application code ───────────────────────────────────────
COPY . .

# ── Create upload directory ─────────────────────────────────────
RUN mkdir -p uploads

# ── Expose port ─────────────────────────────────────────────────
EXPOSE 8000

# ── Run ──────────────────────────────────────────────────────────
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
