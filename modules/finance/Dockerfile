FROM python:3.10-slim

# Metadata
LABEL maintainer="marcin@example.com"
LABEL description="Finance service for Obsidian Brain (Receipts & Expenses)"

# Install system dependencies (Tesseract OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-pol \
    tesseract-ocr-eng \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install shared library
# Assuming the build context is set to module root, we need to mount shared in docker-compose
# For development, we rely on volume mount. For build, we might need it.
# This line assumes shared lib is available or installed in development mode via volume.
# To allow build to succeed without shared context, we comment it out here and rely on runtime volume or proper build context.
# RUN pip install -e /shared

ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; r=redis.Redis(host='redis'); r.ping()" || exit 1

# Run service
CMD ["python", "main.py"]
