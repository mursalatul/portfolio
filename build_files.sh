#!/bin/bash
# Build script for Vercel deployment

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

# Load initial data if DB is empty
python manage.py shell -c "
from core.models import Profile
if not Profile.objects.exists():
    from django.core.management import call_command
    call_command('loaddata', 'initial_data')
    print('Fixtures loaded.')
else:
    print('Data already exists, skipping fixtures.')
"
