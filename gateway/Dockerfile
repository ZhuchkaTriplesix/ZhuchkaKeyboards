FROM cr.yandex/crpu7tvikl80rtk3jn38/python312-alpine-uv-base:latest

WORKDIR /app


COPY . .


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod -R a+rx /app/src/database/alembic


ENV PYTHONPATH=/app/src

# Use tini as entrypoint for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Run migrations and then start the app
CMD sh -c "alembic -c /app/src/database/alembic.ini upgrade head && uvicorn main:app --host 0.0.0.0 --port 8001 --reload --log-level debug"