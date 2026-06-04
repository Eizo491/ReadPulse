from pathlib import Path
import os
import socket

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-ktvdk@s_5s@j3*(c9&vkqd#nzly(1ca2zd!_bskj(nny$5of&%'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'readpulse.pythonanywhere.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'books',
    'django.contrib.sites',    
    'allauth', 
    'allauth.account', 
    'allauth.socialaccount', 
    'allauth.socialaccount.providers.google', 
    'allauth.socialaccount.providers.github', 
    'pwa',
]


if "pythonanywhere" in socket.gethostname():
    SITE_ID = 3
else:
    SITE_ID = 2
 
AUTHENTICATION_BACKENDS = [ 
    'django.contrib.auth.backends.ModelBackend',       
    'allauth.account.auth_backends.AuthenticationBackend', 
] 

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware', 
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ReadPulse.urls'

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

WSGI_APPLICATION = 'ReadPulse.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'          
LOGIN_REDIRECT_URL = '/'                

LOGOUT_REDIRECT_URL = '/accounts/login/'  
ACCOUNT_LOGOUT_REDIRECT_URL = '/'    
ACCOUNT_LOGOUT_ON_GET = True         
# logout immediately on GET 
ACCOUNT_LOGIN_METHODS = {"username", "email"} 
ACCOUNT_SIGNUP_FIELDS = [ 
"username*", 
"email*", 
"password1*", 
"password2*", 
] 

GOOGLE_BOOKS_API_KEY = 'AIzaSyDXKHhFfTasXZrrEDybi-uJqmH3u9qsafY'


PWA_APP_NAME = 'ReadPulse'
PWA_APP_DESCRIPTION = "Your Reading Companion"
PWA_APP_THEME_COLOR = '#0A0A0A'
PWA_APP_BACKGROUND_COLOR = '#FFFFFF'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'portrait'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {
        'src': '/static/img/logo.png',
        'sizes': '192x192'
    },
    {
        'src': '/static/img/logo.png',
        'sizes': '512x512'
    }
]
PWA_APP_ICONS_APPLE = [
    {
        'src': '/static/img/logo.png',
        'sizes': '192x192'
    },
    {
        'src': '/static/img/logo.png',
        'sizes': '512x512'
    }
]
PWA_APP_DIR = 'ltr'
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'static/js', 'serviceworker.js')
