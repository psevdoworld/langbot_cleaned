import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'langbot_db',
        'USER': 'langbot',
        'PASSWORD': 'removed',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },

}

DEBUG = True
STATICFILES_DIRS = []
STATIC_ROOT = os.path.join(BASE_DIR, "static/")



sentry_sdk.init(
    dsn="https://b6c66cb0cae44fa8a7b8ca47082ca13a@o234971.ingest.sentry.io/5216042",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

ADMINS_ID = [65353297, ]
