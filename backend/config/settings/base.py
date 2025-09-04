import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.getenv('SECRET_KEY','dev-secret')
DEBUG = os.getenv('DEBUG','1') == '1'

# More flexible ALLOWED_HOSTS for development
if DEBUG:
    ALLOWED_HOSTS = ['*']  # Allow all hosts in development
else:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

INSTALLED_APPS = [
  'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
  'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
  'rest_framework','corsheaders','drf_spectacular',
  # Feature-first apps
  'apps.common.apps.CommonConfig',
  'apps.users.apps.UsersConfig', 
  'apps.catalog.apps.CatalogConfig',
  'apps.orders.apps.OrdersConfig',
  # Minimal placeholder apps (can be expanded later)
  'apps.payments.apps.PaymentsConfig',
  'apps.activities.apps.ActivitiesConfig', 
  'apps.cart.apps.CartConfig',
  'apps.recommendations.apps.RecommendationsConfig',
]

# Optionally include drf_spectacular_sidecar if installed (provides local swagger assets)
try:
  import drf_spectacular_sidecar  # type: ignore
  INSTALLED_APPS.append('drf_spectacular_sidecar')
except Exception:
  pass

MIDDLEWARE = [
  'corsheaders.middleware.CorsMiddleware',
  'django.middleware.security.SecurityMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
    'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS':{'context_processors':[
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'config.wsgi.application'

# Custom user model
AUTH_USER_MODEL = 'users.User'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

JWT_SECRET = os.getenv('JWT_SECRET', SECRET_KEY)
JWT_ACCESS_TTL_MINUTES = int(os.getenv('JWT_ACCESS_TTL_MINUTES', '15'))
JWT_REFRESH_TTL_DAYS = int(os.getenv('JWT_REFRESH_TTL_DAYS', '7'))

REST_FRAMEWORK = {
  "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
  "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
  "DEFAULT_VERSION": "v1",
  "ALLOWED_VERSIONS": ("v1",),
  "DEFAULT_AUTHENTICATION_CLASSES": [
    "apps.users.auth.SessionCustomerAuthentication",
    "apps.users.auth.JWTAuthentication",
    "rest_framework.authentication.SessionAuthentication",
  ],
  "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
  "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
  "PAGE_SIZE": 20,
}

SPECTACULAR_SETTINGS = {
  "TITLE": "E-commerce API (Cloud DB)",
  "DESCRIPTION": "DRF over existing MariaDB schema: catalog, orders, payments, activities.",
  "VERSION": "1.0.0",
  "SERVE_INCLUDE_SCHEMA": False,
  "SERVERS": [{"url": "http://localhost:8000", "description": "Local"}],
}

# CORS settings for frontend connection (dev)
CORS_ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "http://localhost:3001",
  "http://localhost:3002",
  "http://127.0.0.1:3000",
  "http://127.0.0.1:3001",
  "http://127.0.0.1:3002",
  "http://localhost:8000",
  "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',  # Giảm log level để tiết kiệm memory
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',  # Chỉ log error
            'propagate': False,
        },
        'apps.recommendations': {
            'handlers': ['console'], 
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Memory optimizations
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB limit
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB limit

# Disable debug toolbar and unnecessary middlewares in production
if not DEBUG:
    MIDDLEWARE = [m for m in MIDDLEWARE if 'debug' not in m.lower()]

# Session optimization - use database sessions for memory efficiency  
if not DEBUG:
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    SESSION_COOKIE_AGE = 3600  # 1 hour
else:
    SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# Default language and timezone
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Frontend URL for PayPal redirects
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Use signed cookie session backend to avoid creating django_session table on the
# remote managed database (we don't run migrations against it).
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# PayPal Settings
PAYPAL_SETTINGS = {
    'MODE': os.getenv('PAYPAL_MODE', 'sandbox'),  # 'sandbox' or 'live'
    'CLIENT_ID': os.getenv('PAYPAL_CLIENT_ID', ''),
    'CLIENT_SECRET': os.getenv('PAYPAL_CLIENT_SECRET', ''),
    'SANDBOX_EMAIL': os.getenv('PAYPAL_SANDBOX_EMAIL', ''),
    'WEBHOOK_ID': os.getenv('PAYPAL_WEBHOOK_ID', ''),
}

# Payment Gateway Settings (Legacy)
PAYMENT_GATEWAY = {
    'SANDBOX_MODE': os.getenv('PAYMENT_SANDBOX_MODE', '1') == '1',  # Default to sandbox
    'SANDBOX_BASE_URL': os.getenv('PAYMENT_SANDBOX_URL', 'https://api.sandbox.payments.com'),
    'PRODUCTION_BASE_URL': os.getenv('PAYMENT_PRODUCTION_URL', 'https://api.payments.com'),
    'API_KEY': os.getenv('PAYMENT_API_KEY', 'sandbox_key_test'),
    'WEBHOOK_SECRET': os.getenv('PAYMENT_WEBHOOK_SECRET', 'sandbox_webhook_secret'),
    'SUPPORTED_CURRENCIES': ['VND', 'USD', 'EUR'],
    'DEFAULT_CURRENCY': 'VND',
    'TIMEOUT_SECONDS': int(os.getenv('PAYMENT_TIMEOUT', '30')),
}

# Sandbox-specific settings
if PAYMENT_GATEWAY['SANDBOX_MODE']:
    PAYMENT_GATEWAY.update({
        'SIMULATE_DELAYS': os.getenv('PAYMENT_SIMULATE_DELAYS', '1') == '1',
        'FORCE_SUCCESS': os.getenv('PAYMENT_FORCE_SUCCESS', '0') == '1',  # For testing
        'LOG_ALL_REQUESTS': os.getenv('PAYMENT_LOG_REQUESTS', '1') == '1',
    })
