FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ src/
COPY config.example.yaml ./config.yaml

# Install the package (not editable for production)
RUN pip install --no-cache-dir ".[postgres]"

# Create data directory for SQLite
RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1

CMD ["wallet-watch", "start"]
