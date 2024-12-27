# Use the official Python image as a base
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file to container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . /app/

# Expose the application port
EXPOSE 8000

# Command to run the FastAPI application using uvicorn
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
