#!/bin/bash

# Navigate to the backend directory
cd backend

# Apply database migrations
python3 manage.py migrate

# Collect static files
python3 manage.py collectstatic --noinput

# Start Gunicorn server
gunicorn formCreatorApp.wsgi:application --bind 0.0.0.0:$PORT