#!/bin/bash

echo "Building the project..."
# Create a virtual environment to avoid "externally-managed-environment" error
python3 -m venv venv
source venv/bin/activate

# Install dependencies within the virtual environment
pip install --upgrade pip
pip install -r requirements.txt

# Run collectstatic to generate the staticfiles directory
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Bundle media files into the static output so Vercel CDN can serve them
# We copy them into 'staticfiles/media' so they map to '/media/' URLs
echo "Bundling media files..."
mkdir -p staticfiles/media
if [ -d "media" ]; then
    cp -r media/* staticfiles/media/ || true
fi
