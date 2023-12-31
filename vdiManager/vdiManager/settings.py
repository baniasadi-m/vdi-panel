"""
Django settings for vdiManager project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
from os import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-l*huv-1od@5(g5c%rahds=6apcb11hyh!f9zz1ctc_x!&n=+wz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = environ.get("VDI_PANEL_WHITELIST_IPS").split(",")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vdiApp',
    'adAuth',
    'jalali_date',
    'bootstrapform',
    'accounts',
    'online_users',
    'rest_framework',
    'captcha',
    'drf_yasg',
  
]
########  Captcha Config ###########
CAPTCHA_FONT_SIZE = 35


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'online_users.middleware.OnlineNowMiddleware',
]

ROOT_URLCONF = 'vdiManager.urls'

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

WSGI_APPLICATION = 'vdiManager.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DB ={
    "MYSQL_DB_NAME": environ.get("VDI_MYSQL_DB","panel"),
    "MYSQL_DB_USER":environ.get("VDI_MYSQL_USER","panel"),
    "MYSQL_DB_PASSWORD":environ.get("VDI_MYSQL_PASSWORD","panel"),
    "MYSQL_DB_HOST":environ.get("VDI_MYSQL_HOST","172.17.0.2"),
    "MYSQL_DB_PORT":environ.get("VDI_MYSQL_PORT","3306"),

}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': DB["MYSQL_DB_NAME"],
        'USER': DB["MYSQL_DB_USER"],
        'PASSWORD': DB["MYSQL_DB_PASSWORD"],
        'HOST': DB["MYSQL_DB_HOST"],   # Or an IP Address that your DB is hosted on
        'PORT': DB["MYSQL_DB_PORT"],
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / "statics",
    
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# default settings
JALALI_DATE_DEFAULTS = {
   'Strftime': {
        'date': '%y/%m/%d',
        'datetime': '%H:%M:%S _ %y/%m/%d',
    },
    'Static': {
        'js': [
            # loading datepicker
            'admin/js/django_jalali.min.js',
            # OR
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.core.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/calendar.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc-fa.js',
            # 'admin/js/main.js',
        ],
        'css': {
            'all': [
                'admin/jquery.ui.datepicker.jalali/themes/base/jquery-ui.min.css',
            ]
        }
    },
}

########### App Configs   ##########

class Config:
    DOCKER_DESKTOP_IMAGE = environ.get('VDI_DESKTOP_IMAGE')
    DOCKER_BROWSER_IMAGE = environ.get('VDI_BROWSER_IMAGE')
    Active_Directory_OUName = environ.get('VDI_AD_OUName')
    Active_Directory_GroupName = environ.get('VDI_AD_GroupName')
    Active_Directory_DomainName = environ.get('VDI_AD_DomainName')
    Active_Directory_ServerIP = environ.get('VDI_AD_ServerIP')
    GUNICORN_BIND = environ.get("VDI_GUNICORN_BIND")
    GUNICORN_ACCESS_LOG = environ.get('VDI_ACCESS_LOG_DIR')
    GUNICORN_ERROR_LOG = environ.get('VDI_ERROR_LOG_DIR')
    AGENT_JWT_SECRET = environ.get('AGENT_JWT_SECRET')
    AGENT_JWT_ISSUER = environ.get('AGENT_JWT_ISSUER')    
    AGENT_JWT_ALGO = environ.get('AGENT_JWT_ALGO')    
    VDI_EXPIRY_DAYS = environ.get('VDI_EXPIRY_DAYS','1')    
