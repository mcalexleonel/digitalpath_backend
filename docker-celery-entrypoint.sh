#!/bin/bash
set -e

# Solo esperar por PostgreSQL si DB_HOST está definido (PostgreSQL local)
if [ -n "$DB_HOST" ]; then
  echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
  while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
  done
  echo "PostgreSQL started"
else
  echo "Using external database (Neon), skipping wait..."
fi

echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis started"

echo "Starting Celery worker..."
exec "$@"
