FROM python:3.10-slim

LABEL maintainer="your@email.com"
LABEL description="Refinery AI service for Obsidian Brain"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Note: Shared library is installed at runtime via docker-compose command

ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Health check (check if Redis is available)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; r=redis.Redis(host='redis'); r.ping()" || exit 1

CMD ["python", "main.py"]
