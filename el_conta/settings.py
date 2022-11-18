from pathlib import Path

from django.contrib.messages import constants as messages

try:
    from el_conta.local_settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DATABASES
except ImportError:
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    DATABASES = {}
    print('No local settings found')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-xhr-%=1il%ev_jbne2$u=bc1rp0n@ngb=c%u_%7oa)u(_$=b)p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'elconta.com.ar', 'www.elconta.com.ar', '54.241.109.209']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'widget_tweaks',

    # Own
    'homepage',
    'login',
    'export_lsd',
    'reader',
    'users.apps.UserConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Agregados
    'crum.CurrentRequestUserMiddleware'
]

ROOT_URLCONF = 'el_conta.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'el_conta.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
# Reemplaza esto en el archivo local_settings.py acorde a la base de datos
# que quieres usar (por ejemplo PostgreSQL o MySQL)

if not DATABASES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_L10N = True
pioUSE_TZ = True
USE_THOUSAND_SEPARATOR = True

# more custom folders STATICFILES_DIRS = ['el_conta/static']
STATIC_URL = '/static/'

if DEBUG:
    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]
else:
    STATIC_ROOT = BASE_DIR / 'static'
    
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

TEMP_ROOT = BASE_DIR / 'temp'
TEMP_URL = '/temp/'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'


# Email configs --------------------------------------
# Usar local-settings para actualizar estos valores
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.sendinblue.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
if not EMAIL_HOST_PASSWORD:
    EMAIL_HOST_USER = ''  # definir-en-local-settings.py
    EMAIL_HOST_PASSWORD = ''  # definir-en-local-settings.py
# ------------------------------------------------------

SESSION_COOKIE_AGE = 60 * 60 * 24 * 30

# Sobreescribir las configuraciones necesarias para tu entorno.
# try:
#     from el_conta.local_settings import *
# except ImportError:
#     print('local_settings no encontrado')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logging-info.log',
            'formatter': 'format_function',
        },
        'file_error': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logging-error.log',
            'formatter': 'format_function',
        },
    },
    'formatters': {
        'format_function': {
            'format': '[{pathname}:{name}:{levelname}:{funcName}:{asctime}:{module} {process:d} {thread:d}] {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
    'root': {
        'handlers': ['file_error'],
        'level': 'WARNING',
        'propagate': True,
    },
}

MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
 }
