# Rankivo — SEO AI Tools
# Multi-stage Docker build for production.

# ── Stage 1: Build dependencies ──────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for psycopg2 and numpy builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ── Stage 2: Lean runtime image ──────────────────────
FROM python:3.12-slim

# Runtime libs for psycopg2 + Playwright Chromium dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl wget gnupg fonts-liberation libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdrm2 libgbm1 libgtk-3-0 libnss3 \
    libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 \
    libxrandr2 xdg-utils && \
    rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -s /bin/false appuser

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5500

# Install Python wheels from builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Install Playwright browsers (Chromium) — already in wheels from requirements.txt
ENV PLAYWRIGHT_BROWSERS_PATH=/app/playwright-browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Ownership & user switch
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 5500

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5500/health || exit 1

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5500", "app:app"]
