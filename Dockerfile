# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY core/ ./core/
COPY schemas/ ./schemas/
COPY services/ ./services/
COPY scripts/ ./scripts/
COPY utils/ ./utils/
COPY rag_pipeline.py .
COPY services/document_processor.py .
COPY demo_rag.py .

# Create directories for data
RUN mkdir -p /app/data /app/extracted_images

# Set Python path
ENV PYTHONPATH=/app

# Default command (can be overridden)
CMD ["python", "demo_rag.py"]