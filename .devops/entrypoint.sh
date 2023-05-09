#!/usr/bin/env sh

# Exit in case of error
set -e

echo "Run flask migrations..."
flask db upgrade
echo "Starting flask server..."
gunicorn --bind 0.0.0.0:5000 wsgi:app --workers=4 --timeout=120 --log-level=debug
echo "Done!"
