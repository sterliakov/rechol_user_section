from __future__ import annotations

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

if not DEBUG:
    ALLOWED_HOSTS = [os.getenv("SERVER_NAME")]
    CSRF_TRUSTED_ORIGINS = [f'https://{os.getenv("SERVER_NAME")}']
else:
    ALLOWED_HOSTS = ["*"]
    CSRF_TRUSTED_ORIGINS = ["http://localhost:5173"]

# Application definition

INSTALLED_APPS = [
    # Native
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.postgres",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    # 3rd party
    "ajax_select",
    "bootstrap_datepicker_plus",
    "compressor",
    "django_countries",
    "crispy_forms",
    "django_object_actions",
    "django_select2",
    "django_ses",
    "djangobower",
    "import_export",
    "phonenumber_field",
    "psqlextra",
    "widget_tweaks",
    "dj_rest_auth",
    # 1st party
    "users",
    # dev apps below
    "debug_toolbar",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rechol_user_section.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "root": {
        "handlers": ["console", "mail_admins"],
        "level": "DEBUG",
        "propagate": False,
    },
}

WSGI_APPLICATION = "rechol_user_section.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "psqlextra.backend",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("dj_rest_auth.jwt_auth.JWTCookieAuthentication",)
}
REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "pcho-auth",
    "JWT_AUTH_REFRESH_COOKIE": "pcho-refresh-token",
}

LANGUAGE_CODE = "ru"
LOCALE = "ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
LANGUAGES = (
    ("ru", "Russian"),
    ("en", "English"),
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static_files"
STATICFILES_STORAGE = "compressor.storage.CompressorFileStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = "/var/www/rechol_user_section/media/"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_HOST", "redis://127.0.0.1:6379") + "/0",
        "TIMEOUT": 3600,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "DEFAULT_TIMEOUT": 3600,
        },
    },
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_HOST", "redis://127.0.0.1:6379") + "/1",
        "TIMEOUT": 86400,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "DEFAULT_TIMEOUT": 86400,
        },
    },
    # Used only for django-compressor offline CI
    "filesystem": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/tmp/django_cache",  # noqa: S108
    },
}

CRISPY_TEMPLATE_PACK = "bootstrap4"

BOWER_INSTALLED_APPS = (
    "jquery#3.5.1",  # 3.6.0 results in select2 widget problems
    "bootstrap#4",
    "eonasdan-bootstrap-datetimepicker#4.17.49",
    "jQuery-contextMenu#2.7.1",
    "https://github.com/koalyptus/TableFilter.git",
    "awesomplete",
    "knockout",
    "https://github.com/mdbootstrap/perfect-scrollbar.git",
    "bootstrap-select#1.13.14",
    "moment",
    "https://github.com/dangrossman/daterangepicker.git",
    "humanize-duration",
)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "djangobower.finders.BowerFinder",
    "compressor.finders.CompressorFinder",
)

LOGIN_URL = LOGOUT_REDIRECT_URL = "/profile/login"
LOGIN_REDIRECT_URL = "/profile/update/"

AUTH_USER_MODEL = os.getenv("USER_MODEL", "users.User")

# django-phone-number
PHONENUMBER_DEFAULT_REGION = "RU"
PHONENUMBER_DB_FORMAT = "E164"
PHONENUMBER_DEFAULT_FORMAT = "INTERNATIONAL"

# django-compressor
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_CACHE_BACKEND = os.getenv("COMPRESSOR_CACHE", "default")
COMPRESS_OUTPUT_DIR = "compressed"
# We now depend on dart sass implementation.
# Install with `npm i -g sass`
COMPRESS_PRECOMPILERS = (("text/x-scss", "/usr/local/bin/sass {infile} {outfile}"),)
COMPRESS_FILTERS = {
    "css": ["compressor.filters.css_default.CssAbsoluteFilter"],
    "js": ["compressor.filters.jsmin.JSMinFilter"],
}
LIBSASS_OUTPUT_STYLE = "compressed"
LIBSASS_SOURCE_COMMENTS = False

DATE_INPUT_FORMATS = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d")

# Email
EMAIL_BACKEND = "django_ses.SESBackend"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SES_REGION_NAME = "us-east-2"
AWS_SES_REGION_ENDPOINT = "email.us-east-2.amazonaws.com"
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_SENDER")

# Import-Export
IMPORT_EXPORT_USE_TRANSACTIONS = True
