# Render build script
#!/bin/bash

# Build script for Render deployment
echo "Starting Render build process..."

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build process completed successfully!"
