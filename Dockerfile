# --- Dockerfile (build-time download: model baked into image) ---
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build/system deps, pip-install gdown, and keep apt cache clean
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        git \
        ca-certificates \
    && python -m pip install --no-cache-dir gdown \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Download the model to the container root
# (use --id <fileid> for robustness)
RUN python -m gdown.cli --id 1Q21qT1oRfexrTD0_wCXYvtL4nyC0fFIK -O /model.safetensors

# Copy project files
COPY . .

# Expose port (adjust if needed)
EXPOSE 8000

# Default command (change to gunicorn for production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
