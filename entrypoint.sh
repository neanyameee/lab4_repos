#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
if [ "$DATABASE_URL" != "" ]; then
    while ! python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
        sleep 0.1
    done
else
    echo "Using SQLite - no need to wait for database"
fi
echo "Database is ready"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if doesn't exist (only in development)
if [ "$DEBUG" = "True" ]; then
    echo "Creating superuser..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin/admin')
else:
    print('Superuser already exists')
"
fi

# Start server
echo "Starting server..."
exec "$@"