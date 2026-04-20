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
