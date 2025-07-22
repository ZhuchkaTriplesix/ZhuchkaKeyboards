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
    tini \
    && rm -rf /var/cache/apk/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make alembic scripts executable
RUN chmod -R a+rx /app/src/database/alembic

# Set environment for alembic
ENV PYTHONPATH=/app/src

# Use tini as entrypoint for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Run migrations and then start the app
CMD alembic -c /app/src/database/alembic.ini upgrade head && uvicorn main:app --host 0.0.0.0 --port 8001 --reload --log-level debug