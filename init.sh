#!/bin/bash

# Create database directory
mkdir --parents "./production_data/db/"

# Gather static files
mkdir --parents "./deployment/static_collected/"
pipenv run python manage.py collectstatic --no-input
