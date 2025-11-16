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

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser if not exists..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@digitalpathai.com', 'changeme123')
    print('Superuser created: admin / changeme123')
else:
    print('Superuser already exists')
EOF

echo "Starting server..."
exec "$@"
