import os
from pathlib import Path
from datetime import timedelta


DEBUG = True

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get('SECRET_KEY', 'jf29BphWoc5P5LmRxlK9Dd7h-YxSyjZ-lFS5d74_U0ZxgW17DB0wRA7w1J6x38A')


ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'unachatbot-hxhu.onrender.com']

CORS_ALLOW_ALL_ORIGINS = True

LOGIN_URL = 'login'  # URL to redirect to when login is required
LOGIN_REDIRECT_URL = 'home'  # URL to redirect to after a successful login
LOGOUT_REDIRECT_URL = 'home'  # URL to redirect to after a successful logout


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Homepage',
    'corsheaders',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'ChatBot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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


WSGI_APPLICATION = 'ChatBot.wsgi.application'


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unachatbot_database',
        'USER': 'islam',
        'PASSWORD': '07wAp0JP7mCb5kROa5Vmg0MgGyi1MvY7',
        'HOST': 'dpg-cr22hn8gph6c73beob6g-a.oregon-postgres.render.com',
        'PORT': '5432',
    }
}



# database url = 'postgresql://chatbot_koom_user:CsfbW7W6qyL19F3znzS0D9levGOCR33f@dpg-cqvp8srv2p9s739fiac0-a/chatbot_koom'


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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Azure OpenAI Configuration
# settings.py

# Azure OpenAI Configuration

