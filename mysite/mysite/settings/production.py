import os
from .base import *
import environ

env = environ.Env()
environ.Env.read_env()

DEBUG = False

ALLOWED_HOSTS = ['inventory', 'www.inventory']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True

# Additional Settings
SECURE_HSTS_SECONDS = 3600

SECURE_HSTS_PRELOAD = True

SECURE_HSTS_INCLUDE_SUBDOMAINS = True