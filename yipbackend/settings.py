from pathlib import Path
import os
from dotenv import load_dotenv
from decouple import config as decouple_config

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = decouple_config('SECRET_KEY')

DEBUG = decouple_config('DEBUG',bool)

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'api',
    'db'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     'corsheaders.middleware.CorsMiddleware',
     'yipbackend.middlewares.UniversalErrorHandlerMiddleware'
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'yipbackend.urls'

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

WSGI_APPLICATION = 'yipbackend.wsgi.application'

DATABASES = {
   "default": {
       "ENGINE": decouple_config("DATABASE_ENGINE","django.db.backends.mysql"),
       "NAME": decouple_config("DATABASE_NAME"),
       "USER": decouple_config("DATABASE_USER"),
       "PASSWORD": decouple_config("DATABASE_PASSWORD"),
       "HOST": decouple_config("DATABASE_HOST"),
       "PORT": decouple_config("DATABASE_PORT"),
   }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'utils.authentication.JWTAuthentication',
    ]
}

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'request_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': decouple_config("LOGGER_DIR_PATH") + '/request.log',
            'formatter': 'verbose',
        },
        'error_log': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': decouple_config("LOGGER_DIR_PATH") + '/error.log',
            'formatter': 'verbose',
        },
        'sql_log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': decouple_config("LOGGER_DIR_PATH") + '/sql.log',
            'formatter': 'verbose',
        },
        'root_log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': decouple_config("LOGGER_DIR_PATH") + '/root.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['request_log'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['error_log'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['sql_log'],
            'level': 'DEBUG',
            'propagate': True,
        },
        '': {
            'handlers': ['root_log'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
    },
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_ROOT=os.path.join(BASE_DIR, "staticfiles","static")

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AUTH_USER_MODEL = "api.CustomUser"

JWT_CONF = {
  "TOKEN_LIFETIME_HOURS":240
}
