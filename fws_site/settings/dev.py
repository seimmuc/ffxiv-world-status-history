SECRET_KEY = 'django-insecure-r+)5=oi&-r+28%xy&d9ov8x!sw8948i7frx2vr)e&d)b%258tm'
DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ffxiv_world_status_history_dev',
        'USER': 'fwshd',
        'PASSWORD': 'fwshd_pass',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 30,
        'CONN_HEALTH_CHECKS': False
    }
}

CELERY_BROKER_URL = 'amqp://fwshd:fwshd_pass@localhost:5672/fwsvhost'
CELERY_RESULT_BACKEND = 'rpc://fwshd:fwshd_pass@localhost:5672/fwsvhost'
