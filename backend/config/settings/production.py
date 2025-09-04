"""
Production settings for Render deployment
"""
import os
from .base import *

# Safe import for production dependencies
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# Security
DEBUG = int(os.environ.get('DEBUG', 0))
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-this')

# Hosts - theo gợi ý Render
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'ecomtech.onrender.com,localhost,127.0.0.1').split(',')

# CSRF và CORS - theo gợi ý
CSRF_TRUSTED_ORIGINS = [
    'https://ecomtech.onrender.com',
] + os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if os.environ.get('CSRF_TRUSTED_ORIGINS') else ['https://ecomtech.onrender.com']

CORS_ALLOWED_ORIGINS = [
    'https://ecomtech-domain.tld',  # Frontend Vercel domain
] + os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if os.environ.get('CORS_ALLOWED_ORIGINS') else ['https://ecomtech-domain.tld']

# Backend URL for image generation
BACKEND_URL = os.environ.get('BACKEND_URL', 'https://ecomtech.onrender.com')

# Frontend URL for PayPal redirects
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://ecomtech-domain.tld')

# Database - Support both DATABASE_URL and individual credentials
if os.environ.get('DATABASE_URL') and dj_database_url:
    # Parse DATABASE_URL (format: mysql://USER:PASS@HOST:PORT/DB)
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Fallback to individual credentials
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'bookverse'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }

# CORS settings for frontend
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.vercel.app",  # Replace with your Vercel domain
    "http://localhost:3000",  # For local development
]

CORS_ALLOW_CREDENTIALS = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
