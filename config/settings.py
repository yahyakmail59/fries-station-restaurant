from pathlib import Path
import os
import sys

from django.core.exceptions import ImproperlyConfigured

try:
    import dj_database_url
except ImportError:  # Allows basic local checks before installing optional production packages.
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-only-change-me')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
if not DEBUG and SECRET_KEY == 'dev-only-change-me':
    raise ImproperlyConfigured(
        'DJANGO_SECRET_KEY must be set to a long random value when DJANGO_DEBUG=0.'
    )
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'restaurant',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Compress dynamic HTML/JSON responses. Static assets are compressed by
    # collectstatic and served directly by PythonAnywhere.
    'django.middleware.gzip.GZipMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # Generates ETags so repeat visits can receive a small 304 response.
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DB_CONN_MAX_AGE = int(os.environ.get('DJANGO_DB_CONN_MAX_AGE', '240'))
if dj_database_url and os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=DB_CONN_MAX_AGE,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            # Wait briefly instead of failing immediately when the cashier and
            # an online order write at the same moment.
            'OPTIONS': {
                'timeout': int(os.environ.get('DJANGO_SQLITE_TIMEOUT', '20')),
            },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Gaza'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    # Manifest storage adds a content hash to every static file name, so browser
    # caches invalidate automatically on deploy (no manual ?v= query strings).
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
if AWS_STORAGE_BUCKET_NAME:
    STORAGES['default'] = {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'bucket_name': AWS_STORAGE_BUCKET_NAME,
            'region_name': os.environ.get('AWS_S3_REGION_NAME') or None,
            'endpoint_url': os.environ.get('AWS_S3_ENDPOINT_URL') or None,
            'custom_domain': os.environ.get('AWS_S3_CUSTOM_DOMAIN') or None,
            'default_acl': None,
            'file_overwrite': False,
            'querystring_auth': os.environ.get('AWS_QUERYSTRING_AUTH', '0') == '1',
            'object_parameters': {'CacheControl': 'max-age=86400'},
        },
    }
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 365 if not DEBUG else 0
if 'test' in sys.argv:
    # Tests run with DEBUG=False and no collectstatic manifest; use plain storage.
    STORAGES['staticfiles'] = {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('DJANGO_MEDIA_ROOT', BASE_DIR / 'media'))
SERVE_MEDIA = os.environ.get('DJANGO_SERVE_MEDIA', '1' if DEBUG else '0') == '1'
if AWS_STORAGE_BUCKET_NAME:
    SERVE_MEDIA = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# One PythonAnywhere worker uses an in-process cache efficiently. cached_db
# sessions remain valid after a reload because Django falls back to the DB.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': os.environ.get('DJANGO_CACHE_LOCATION', 'b12-restaurant'),
        'TIMEOUT': int(os.environ.get('DJANGO_CACHE_TIMEOUT', '300')),
        'OPTIONS': {
            'MAX_ENTRIES': int(os.environ.get('DJANGO_CACHE_MAX_ENTRIES', '2000')),
            'CULL_FREQUENCY': 3,
        },
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

# Optional email notifications for new reservations. Leave DJANGO_EMAIL_HOST
# empty to disable silently. On PythonAnywhere free accounts only smtp.gmail.com
# is reachable (requires a Gmail App Password).
EMAIL_HOST = os.environ.get('DJANGO_EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('DJANGO_EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('DJANGO_EMAIL_USE_TLS', '1') == '1'
DEFAULT_FROM_EMAIL = os.environ.get('DJANGO_DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'webmaster@localhost')
RESERVATION_NOTIFY_EMAIL = os.environ.get('DJANGO_RESERVATION_NOTIFY_EMAIL', '')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
TRUSTED_PROXY_HOPS = int(os.environ.get('DJANGO_TRUSTED_PROXY_HOPS', '0'))
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', '0') == '1'
SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', '0') == '1'
SECURE_HSTS_PRELOAD = os.environ.get('DJANGO_SECURE_HSTS_PRELOAD', '0') == '1'
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DJANGO_FILE_UPLOAD_MAX_MEMORY_SIZE', str(5 * 1024 * 1024)))
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DJANGO_DATA_UPLOAD_MAX_MEMORY_SIZE', str(8 * 1024 * 1024)))
