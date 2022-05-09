"""
Django settings for jobsearchvn project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
# 
from dotenv import load_dotenv
from datetime import timedelta
from pathlib import Path
import django_heroku

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'taggit',
    's3direct',
    # 
    'api.users',
    'api.members',
    'api.employers',
    'api.jobs',
    'api.searches',
    'api.cvs',
    'api.chats',
    'api.reviews',
    'api.blogs',
    'api.analytics',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', #It was placed on the top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # add this line
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jobsearchvn.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jobsearchvn.wsgi.application'

AUTH_USER_MODEL = 'users.User'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ['DB_ENGINE'],
        'NAME':  os.environ['DB_NAME'],
        'USER':  os.environ['DB_USER'],
        'PASSWORD':  os.environ['DB_PASSWORD'],
        'HOST':  os.environ['DB_HOST'],
        'PORT':  os.environ['DB_PORT'],
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

LANGUAGES = (
    ("en", "English"),
    ("da", "Danish"),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATICFILES_DIRS = [os.path.join(PROJECT_DIR, 'static')]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
django_heroku.settings(locals())

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (        
        'rest_framework_simplejwt.authentication.JWTAuthentication', 
    ),
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PAGINATION_CLASS': 'api.users.custom_pagination.CustomPagination',
    'PAGE_SIZE': 10,    
}


# CORS_ORIGIN_WHITELIST = [
#     'http://localhost:8080',
#     'http://localhost:8000',
#     'http://localhost:3000',
#     'http://127.0.0.1:3000',
#     'https://storage.googleapis.com',
#     'https://googleapis.com',
# ] # If this is used, then not need to use `CORS_ORIGIN_ALLOW_ALL = True`

# CORS_ORIGIN_REGEX_WHITELIST = [
#     'http://localhost:8080',
#     'http://localhost:8000',
#     'http://localhost:3000',
#     'http://127.0.0.1:3000',
#     'https://storage.googleapis.com',
#     'https://googleapis.com',
# ]

# CORS_ALLOWED_ORIGIN_REGEXES = [
#     r"^https://storage.googleapis.com$",
#     r"^https://googleapis.com$",
# ]

CORS_ORIGIN_ALLOW_ALL = True

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=40),
}

GROUP_NAME = {
    'ADMIN': 'admin_group',
    'EMPLOYER': 'employer_group',
    'MEMBER': 'member_group'
}

FRONTEND_SITE_URL=os.getenv('FRONTEND_URL')
FRONTEND_SITE_URL_LOGIN=os.getenv('FRONTEND_URL') + "/login"
FRONTEND_SITE_URL_REGISTER_URL=os.getenv('FRONTEND_URL') + "/sign-up"
FRONTEND_SITE_URL_ACTIVE_ACCOUNT=os.getenv('FRONTEND_URL') + "/active-account/"
FRONTEND_SITE_URL_RESET_PASSWORD=os.getenv('FRONTEND_URL') + "/reset-password/"
# FRONTEND_SITE_URL_VIEW_RECIPE=os.getenv('FRONTEND_URL') + "/recipes"
# FRONTEND_SITE_URL_SHARE_RECIPE=os.getenv('FRONTEND_URL') + "/public-recipe"
# FRONTEND_SITE_URL_REQUEST_RECIPE=os.getenv('FRONTEND_URL') + "/public-create"
# FRONTEND_SITE_URL_CREATE_RECIPE=os.getenv('FRONTEND_URL') + "/create-recipe"

# Email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_FROM = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Cloudinary config
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUD_NAME'),
    'API_KEY': os.getenv('API_KEY'),
    'API_SECRET': os.getenv('API_SECRET')
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Stream chat