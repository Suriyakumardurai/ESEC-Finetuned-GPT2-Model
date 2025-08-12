# --- Dockerfile ---
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps & gdown
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

# Download model from Google Drive with retries
RUN for i in 1 2 3; do \
        gdown --fuzzy "https://drive.google.com/file/d/1Q21qT1oRfexrTD0_wCXYvtL4nyC0fFIK/view?usp=sharing" -O /app/model.safetensors && break || sleep 5; \
    done \
    && test -f /app/model.safetensors || (echo "Model download failed!" && exit 1)
# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Run the app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
