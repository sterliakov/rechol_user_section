from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import boto3

BASE_DIR = Path(__file__).resolve().parent.parent

ENVIRONMENT = os.getenv("ENVIRONMENT", "production").lower()
assert ENVIRONMENT in {"dev", "ci", "build", "production"}, (
    f"Unknown environment: {ENVIRONMENT}"
)
DEVELOPMENT = ENVIRONMENT != "production"
DEBUG = DEVELOPMENT and os.getenv("DEBUG", "False").lower() == "true"


def _get_secret(secret_path: str) -> dict[str, Any]:
    _secret_manager = boto3.client(service_name="secretsmanager")
    response = _secret_manager.get_secret_value(SecretId=secret_path)
    return json.loads(response["SecretString"])


if DEVELOPMENT:
    _secret = {
        "secret_key": "123456",
        "email_sender": "noreply@chemolymp.ru",
        "db_name": os.getenv("POSTGRES_DB"),
        "db_user": os.getenv("POSTGRES_USER"),
        "db_password": os.getenv("POSTGRES_PASSWORD"),
        "db_host": os.getenv("POSTGRES_HOST"),
        "db_port": os.getenv("POSTGRES_PORT"),
        "media_location": "dev",
    }
else:
    _secret_name = os.getenv("SECRET_NAME")
    assert _secret_name is not None
    _secret = _get_secret(_secret_name)

SECRET_KEY = _secret["secret_key"]

if DEVELOPMENT:
    ALLOWED_HOSTS = ["*"]
else:
    _server_name = os.getenv("SERVER_NAME")
    assert _server_name
    ALLOWED_HOSTS = [_server_name]
    CSRF_TRUSTED_ORIGINS = [f"https://{_server_name}"]

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
    "collectfasta",  # must come before staticfiles
    "django.contrib.staticfiles",
    # 3rd party
    "bootstrap_datepicker_plus",
    "concurrency",
    "compressor",
    "django_countries",
    "crispy_forms",
    "django_object_actions",
    "django_ses",
    "import_export",
    "phonenumber_field",
    "widget_tweaks",
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
    "root": {
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        "handlers": ["console"],
    },
    "formatters": {
        "verbose": {
            "format": "[%(levelname)s] %(asctime)s %(module)s:%(lineno)d %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
}

for name in ["boto", "urllib3", "s3transfer", "boto3", "botocore", "nose"]:
    boto3.set_stream_logger(name, logging.WARNING)

DATABASES = {
    "default": {
        "ENGINE": "django_cockroachdb",
        "NAME": _secret["db_name"],
        "USER": _secret["db_user"],
        "PASSWORD": _secret["db_password"],
        "HOST": _secret["db_host"],
        "PORT": _secret["db_port"],
        "OPTIONS": {},
    },
}
if DEVELOPMENT:
    del DATABASES["default"]["PASSWORD"]
else:
    DATABASES["default"]["OPTIONS"] |= {
        "sslmode": "verify-full",
        "sslrootcert": "/certs/ca.crt",
    }
DISABLE_COCKROACHDB_TELEMETRY = True

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


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

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/tmp/django_cache",  # noqa: S108
    },
}

CRISPY_TEMPLATE_PACK = "bootstrap4"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

LOGIN_URL = LOGOUT_REDIRECT_URL = "/profile/login/"
LOGIN_REDIRECT_URL = "/profile/update/"

AUTH_USER_MODEL = "auth.User" if ENVIRONMENT == "build" else "users.User"

# django-phone-number
PHONENUMBER_DEFAULT_REGION = "RU"
PHONENUMBER_DB_FORMAT = "E164"
PHONENUMBER_DEFAULT_FORMAT = "INTERNATIONAL"

# django-compressor
COMPRESS_URL = STATIC_URL = "https://rechol-static.s3.amazonaws.com/"
STATIC_PREFIX = "static"
STATIC_ROOT = BASE_DIR / "static_files"
COMPRESS_ROOT = STATIC_ROOT
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": "rechol-private",  # TODO: move bucket names to config
            "querystring_expire": 8 * 60 * 60,
            "file_overwrite": False,
            "location": _secret["media_location"],
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": "rechol-static",
            "querystring_auth": False,
            "file_overwrite": False,
            "location": STATIC_PREFIX,
        },
    },
    # We only use this to feed static files to django-compressor
    "staticfiles_local": {
        "BACKEND": "compressor.storage.CompressorFileStorage",
        "OPTIONS": {
            "location": COMPRESS_ROOT / STATIC_PREFIX,
        },
    },
    "compressor": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": "rechol-static",
            "querystring_auth": False,
            "file_overwrite": False,
            "location": STATIC_PREFIX,
        },
    },
}
if os.getenv("STATIC_COMPRESS"):
    STORAGES["staticfiles"] = STORAGES["staticfiles_local"]
    COLLECTFASTA_ENABLED = False

COMPRESS_OFFLINE_MANIFEST_STORAGE_ALIAS = COMPRESS_STORAGE_ALIAS = "compressor"
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_OUTPUT_DIR = "compressed"
# django_libsass fails to compile bootstrap and uses deprecated c++ libsass anyway
_SASS_EXECUTABLE = os.getenv("SASS_EXECUTABLE", "")
COMPRESS_PRECOMPILERS = (("text/x-scss", _SASS_EXECUTABLE + " {infile} {outfile}"),)
COMPRESS_FILTERS = {
    "css": ["compressor.filters.css_default.CssAbsoluteFilter"],
    "js": ["compressor.filters.jsmin.JSMinFilter"],
}

COLLECTFASTA_THREADS = 20
COLLECTFASTA_STRATEGY = "collectfasta.strategies.boto3.Boto3Strategy"

DATE_INPUT_FORMATS = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d")

# Email
EMAIL_BACKEND = "django_ses.SESBackend"
AWS_SES_REGION_NAME = "us-east-2"
AWS_SES_REGION_ENDPOINT = f"email.{AWS_SES_REGION_NAME}.amazonaws.com"
DEFAULT_FROM_EMAIL = _secret["email_sender"]

# Import-Export
IMPORT_EXPORT_USE_TRANSACTIONS = True
