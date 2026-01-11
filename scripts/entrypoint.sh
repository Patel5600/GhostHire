#!/bin/bash
set -e

# Wait for DB?
# ./wait-for-it.sh db:5432

# Run migrations
# alembic upgrade head
# For now, using init_db script logic if accessible, or relying on app startup

# Start application
if [ "$1" = 'backend' ]; then
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
elif [ "$1" = 'worker' ]; then
    exec celery -A app.core.celery_app worker --loglevel=info -c 2
fi

exec "$@"
