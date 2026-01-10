# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn[standard] fastapi

# Copy ALL application code
COPY . .

# Create directories for data
RUN mkdir -p /app/data /app/extracted_images /app/data/uploads

# Set Python path
ENV PYTHONPATH=/app

# Run FastAPI app (using routes/main.py as entry point)
CMD ["python", "-m", "uvicorn", "routes.main:app", "--host", "0.0.0.0", "--port", "8000"]