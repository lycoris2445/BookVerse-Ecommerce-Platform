#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting Render build process..."

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.production

# Run migrations
echo "Running database migrations..."
python manage.py migrate --settings=config.settings.production

echo "Build completed successfully!"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build process completed successfully!"
