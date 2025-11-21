# Multi-stage Dockerfile for YOLOX API
# Stage 1: Base image with dependencies
FROM python:3.10-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies in correct order
# Step 1: Install PyTorch first (required by YOLOX)
COPY requirements-base.txt .
RUN pip install --no-cache-dir -r requirements-base.txt

# Step 2: Install main dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 3: Install YOLOX (requires torch to be already installed)
RUN pip install --no-cache-dir git+https://github.com/Megvii-BaseDetection/YOLOX.git

# Stage 2: Production image
FROM base as production

# Copy application code
COPY app/ ./app/
COPY models/ ./models/

# Create non-root user for security
RUN useradd -m -u 1000 apiuser && \
    chown -R apiuser:apiuser /app

USER apiuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')" || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
