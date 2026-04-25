#!/bin/bash
set -e

echo "Waiting for Postgres..."
until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  sleep 1
done

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo " - Inicializar o actualizar tablas base tablas"
if [ "$ENV" != "local-dev" ]; then
  if ! bash /run_all_inits.sh; then
    echo "❌ Error en run_all_inits.sh"
    exit 1
  fi
fi

echo "✅ Database ready!"

# Start server depending on environment
if [ "$ENV" = "local-dev" ]; then
  echo "Starting Django dev server..."
  exec python manage.py runserver 0.0.0.0:8000
else
  # Write a JSON file with the current commit hash and the python version
  echo " - Writing version file"
  VERSION_PATH=/app/version.json
  APP_VERSION=$(cat /usr/local/etc/app_version 2>/dev/null || echo "0.0.0-dev")
  echo "{\"commit\": \"${GIT_COMMIT}\", \"version\": \"${APP_VERSION}\", \"python\": \"$(python --version | awk '{print $2}')\", \"built_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\", \"env\": \"${ENV}\"}" > $VERSION_PATH


  echo "Starting Gunicorn in $ENV mode..."
  exec gunicorn el_conta.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers=1 \
    --threads=2 \
    --timeout=120 \
    --access-logfile - \
    --error-logfile -
fi
