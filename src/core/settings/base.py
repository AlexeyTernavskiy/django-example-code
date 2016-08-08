# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""Common settings and globals."""

from genericpath import exists
from os import mkdir
from os.path import abspath, basename, dirname, join, normpath
from sys import path

# PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))
# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)
# Absolute filesystem path to the project folder:
PROJECT_ROOT = dirname(SITE_ROOT)
# Site name:
SITE_NAME = basename(DJANGO_ROOT)
# Add our project to our python path, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
# END PATH CONFIGURATION


# SECRET CONFIGURATION
# Note: This key should only be used for development and testing.
SECRET_KEY = '1+dca=%8n6#4pc6+y==26h7!7!5ersy&-p+)#&i2tt5ib%48!q'
# END SECRET CONFIGURATION


# SITE CONFIGURATION
# Hosts/domain names that are valid for this site
ALLOWED_HOSTS = []
# END SITE CONFIGURATION

# MANAGER CONFIGURATION
ADMINS = (
    ('', ''),
)
MANAGERS = ADMINS
# END MANAGER CONFIGURATION


# DEBUG CONFIGURATION
DEBUG = False
# END DEBUG CONFIGURATION


# APP CONFIGURATION
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'src.apps.product',
]

INSTALLED_APPS = DJANGO_APPS
# END APP CONFIGURATION


# MIDDLEWARE CONFIGURATION
MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
# END MIDDLEWARE CONFIGURATION

# TEMPLATE CONFIGURATION
APP_DIRS = True

T_CONTEXT_PROCESSORS = (
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

T_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

T_DIRS = (
    normpath(join(SITE_ROOT, 'templates')),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': T_DIRS,
        'APP_DIRS': APP_DIRS,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': T_CONTEXT_PROCESSORS,
        },
    },
]
# END TEMPLATE CONFIGURATION

# URL CONFIGURATION
ROOT_URLCONF = 'src.{0}.urls'.format(SITE_NAME)
# END URL CONFIGURATION


# WSGI CONFIGURATION
WSGI_APPLICATION = '{0}.{1}.wsgi.application'.format(basename(SITE_ROOT), SITE_NAME)
# END WSGI CONFIGURATION


# DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
# END DATABASE CONFIGURATION

# PASSWORD VALIDATION CONFIGURATION
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
# END PASSWORD VALIDATION CONFIGURATION


# INTERNATIONALIZATION CONFIGURATION
TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True
# END INTERNATIONALIZATION CONFIGURATION

# MEDIA CONFIGURATION
MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))

MEDIA_URL = '/media/'
# END MEDIA CONFIGURATION


# STATIC FILE CONFIGURATION
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    normpath(join(SITE_ROOT, 'static'))
]
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
# END STATIC FILE CONFIGURATION


# LOGGING CONFIGURATION
DEBUG_ROOT = normpath(join(PROJECT_ROOT, 'logs'))

if not exists(DEBUG_ROOT):
    mkdir(DEBUG_ROOT)

django_development_file = normpath(join(DEBUG_ROOT, 'django_development.log'))
django_production_file = normpath(join(DEBUG_ROOT, 'django_production.log'))
django_debug_file = normpath(join(DEBUG_ROOT, 'django_debug.log'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'main_formatter': {
            'format': '%(levelname)s:%(name)s: %(message)s'
                      '(%(asctime)s; %(filename)s:%(lineno)d)',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },

    'handlers': {
        'console': {
            'level': 'WARNING',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter'
        },
        'production_logfile': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 7,
            'filename': django_production_file,
            'formatter': 'main_formatter'
        },
        'development_logfile': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 7,
            'filename': django_development_file,
            'formatter': 'main_formatter'
        },
        'debug_logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 3,
            'filename': django_debug_file,
            'formatter': 'main_formatter'
        },
    },

    'loggers': {
        'django': {
            'handlers': ['console', 'development_logfile', 'production_logfile'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'development_logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['console', 'development_logfile'],
            'propagate': False,

        },
        'django.db.backends': {
            'handlers': ['debug_logfile'],
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['development_logfile'],
            'propagate': False,
        },
        '': {
            'handlers': ['debug_logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
