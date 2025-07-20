#!/bin/sh

echo "Waiting for database..."
sleep 5

echo "Running database migrations..."
cd /app
alembic upgrade head

echo "Migrations completed!" 