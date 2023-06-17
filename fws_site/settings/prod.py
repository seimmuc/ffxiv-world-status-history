# Any secret settings should be kept in the separate prod_secrets.py file
# DO NOT import anything from prod_secrets.py here, instead that is done by __init__.py
# This file is also being imported by test.py, but prod_secrets.py is not

import os


DEBUG = False

ALLOWED_HOSTS = ['localhost', 'ffxivws']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'fws',
        'PASSWORD': 'fws_pass',
        'NAME': 'fws',
        'HOST': os.getenv('FWSWEB_DB_HOST', default='localhost'),
        'PORT': '5432',
        'CONN_MAX_AGE': 300,
        'CONN_HEALTH_CHECKS': True
    }
}

CELERY_BROKER_URL = 'amqp://fws:fws_pass@rabbitmq:5672/fws_vhost'
CELERY_RESULT_BACKEND = 'rpc://fws:fws_pass@rabbitmq:5672/fws_vhost'
