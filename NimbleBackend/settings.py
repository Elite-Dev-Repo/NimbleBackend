"""
Django settings for NimbleBackend project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
import dj_database_url # Add this to your requirements.txt

load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", 'django-insecure-(uc*9@2t)0kud_ztwfhql@0q7&97s3n7bkp7o_!c25vt7w&2+*')

DEBUG = os.getenv("DEBUG", "False") == "True"

# --- HOST CONFIGURATION ---
# This ensures both your local env and Vercel are allowed
ALLOWED_HOSTS = [
    'nimble-backend-gamma.vercel.app',
    'localhost',
    '127.0.0.1',
]

# Add Vercel's dynamic deployment URL if it exists
if os.getenv("VERCEL_URL"):
    ALLOWED_HOSTS.append(os.getenv("VERCEL_URL"))

# Paystack configuration
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")
PAYSTACK_CALLBACK_URL = os.getenv("PAYSTACK_CALLBACK_URL")
PAYSTACK_WEBHOOK_SECRET = os.getenv("PAYSTACK_WEBHOOK_SECRET")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', 
    'store',
    'corsheaders',
    'rest_framework_simplejwt',
    'django_filters',
    'payments',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Add this for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'NimbleBackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'NimbleBackend.wsgi.application'

# --- DATABASE CONFIGURATION ---
# Use SQLite for local, but a real DB for Vercel
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# If DATABASE_URL is found (Vercel/Neon/Railway), use it
if os.getenv("DATABASE_URL"):
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Required for Vercel

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- CORS & CSRF CONFIGURATION ---
CORS_ALLOW_CREDENTIALS = True

# Front-end URLs that are allowed to talk to this API
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://127.0.0.1:5173",
    "https://nimble-backend-gamma.vercel.app", # The backend itself for the Browsable API
]

# Important for POST/PUT requests
CSRF_TRUSTED_ORIGINS = [
    FRONTEND_URL,
    "https://nimble-backend-gamma.vercel.app",
]