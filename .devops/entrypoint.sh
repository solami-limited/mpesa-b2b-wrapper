#!/usr/bin/env sh

# Exit in case of error
set -e

echo "Connecting to #$DB_HOST:$DB_PORT..."
# Ping database until it is ready
until nc -z -v -w30 "$DB_HOST" "$DB_PORT"
do
  echo "Waiting for database connection..."
  # wait for 5 seconds before check again
  sleep 5
done

echo "Run flask migrations..."
flask db upgrade
echo "Starting flask server..."
gunicorn --bind 0.0.0.0:5000 wsgi:app --workers=4 --timeout=120 --log-level=debug
echo "Done!"
