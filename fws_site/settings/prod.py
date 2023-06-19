# Any secret settings should be kept in the separate prod_secrets.py file
# DO NOT import anything from prod_secrets.py here, instead that is done by __init__.py
# This file is also being imported by test.py, but prod_secrets.py is not

import os


DEBUG = False

ALLOWED_HOSTS = ['localhost', 'ffxivstatus', 'ffxivstatus.sei.place']
CSRF_TRUSTED_ORIGINS = ['https://ffxivstatus.sei.place']
CSRF_COOKIE_DOMAIN = 'ffxivstatus.sei.place'


# Comment out the following section if not using https
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# Extra security, it's recommended to enable once you're certain everything works well
# SECURE_HSTS_SECONDS = int(60 * 60 * 24 * 365.25)
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

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
