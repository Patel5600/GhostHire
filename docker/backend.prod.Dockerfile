
FROM python:3.10-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies for build
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final Stage
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies and Playwright deps
# Playwright needs specific system libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

# Install Playwright browsers (Chromium only to save space)
RUN pip install playwright && \
    playwright install chromium --with-deps

COPY . .

# Create non-root user
# RUN useradd -m appuser && chown -R appuser /app
# USER appuser 
# (Playwright sometimes has issues with specific non-root setups without complex config, keeping root or assuming mostly compatible for now, but best practice is non-root)

EXPOSE 8000
