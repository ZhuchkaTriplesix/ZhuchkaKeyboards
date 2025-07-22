# Use an official Python runtime as a parent image
FROM python:3.13.3-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql17-dev \
    curl \
    && rm -rf /var/cache/apk/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make migration script executable (если понадобится)
RUN chmod -R a+rx /app/src/database/alembic

# Set work directory to src/database for alembic
WORKDIR /app/src/database
ENV PYTHONPATH=/app/src

# Для запуска приложения по умолчанию (оставляем как есть)
WORKDIR /app/src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--log-level", "debug"]