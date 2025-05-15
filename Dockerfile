FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for OpenCV and other ML libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create the directory structure
RUN mkdir -p backend

# Copy backend code
COPY backend/ backend/

# Create directories for uploads, segmentations, and heatmaps if they don't exist
RUN mkdir -p backend/public/images/uploads backend/public/images/segmentations backend/public/images/heatmaps

# Expose port for FastAPI
EXPOSE 8000

# Set environment variables (these should be provided at runtime in production)
ENV PYTHONPATH=/app

# Run FastAPI with uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"] 