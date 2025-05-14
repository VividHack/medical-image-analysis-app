# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables for better Python behavior in Docker
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# Define a home directory for the app for easier reference
ENV APP_HOME=/opt/app

# Create and set the working directory
WORKDIR $APP_HOME

# Install system dependencies if needed by your Python packages
# For example, if opencv-python needs additional system libraries not covered by its wheel:
# RUN apt-get update && apt-get install -y --no-install-recommends libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*
# For now, this is commented out. Add specific libraries if installation issues arise.

# Install Python dependencies
# Copy requirements.txt first to leverage Docker's layer caching.
# Assumes requirements.txt is at the root of the build context (your project root).
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
# This copies the 'app' directory from your project root (the build context)
# into the '$APP_HOME/app' directory inside the image.
COPY ./app ./app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the Uvicorn server
# This will execute: uvicorn app.main:app --host 0.0.0.0 --port 8000
# 'app.main:app' tells Uvicorn to look for an 'app' instance
# in the 'main.py' file within the 'app' directory (relative to WORKDIR /opt/app).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 