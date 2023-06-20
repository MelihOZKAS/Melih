"""
Django settings for Site project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import environ

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True
env = environ.Env(DEBUG=(bool,False))

environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = env('DEBUG')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')




ALLOWED_HOSTS = env('ALLOWED_HOST',cast=list)

CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS',cast=list)




# Application definition

INSTALLED_APPS = [

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'kontor.apps.KontorConfig',
    'storages',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates']
        ,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "Site.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {

    'default': env.db()

}

#SUBDOMAIN_URLCONFS = {
#    'bayi': 'bayi.urls',
#}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'tr-tr'

TIME_ZONE = "Europe/Istanbul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


STATICFILES_DIRS = [
    BASE_DIR / "static"
]
#if DEBUG:
#    STATIC_URL = "/static/"
#    STATIC_ROOT = BASE_DIR / "staticfiles"
#
#    MEDIA_URL = "/media/"
#    MEDIA_ROOT = BASE_DIR / "media"
#
#    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
#else:
#    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
#    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
#    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
#    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
#
#
#
#    DEFAULT_FILE_STORAGE = 'Site.costum_storages.MediaStorage'
#    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#
#
#    AWS_DEFAULT_ACL = 'public-read'
#    AWS_S3_OBJECT_PARAMETERS = {
#        'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
#        'CacheControl': 'max-age=94608000'
#    }
#
#    STATIC_URL = f'http://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'
#    STATIC_ROOT = STATIC_URL
#    MEDIA_LOCATION = 'media'
#    Resim_kayit_yeri = MEDIA_LOCATION + '/resimler'
#    Dosya_kayit_yeri = MEDIA_LOCATION + '/dosyalar'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
