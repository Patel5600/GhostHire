# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
# Playwright and generic build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project requirements
COPY requirements.txt .

# Install python dependencies
# Note: scikit-learn/pandas can take time to build on slim, but wheels usually available.
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only)
RUN playwright install --with-deps chromium

# Copy project
COPY . .

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
