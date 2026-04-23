from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

SERVICE_NAME = env("SERVICE_NAME", default="core_api")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "accounts",
    "images",
]

MIDDLEWARE = [
    "shared.logging.django.DjangoRequestContextMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core_api.wsgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://postgres:postgres@postgres:5432/portable_pug",
    ),
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Portable Pug Core API",
    "DESCRIPTION": "Auth, image upload, and AI dispatch endpoints.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

JWT_PRIVATE_KEY_PATH = env(
    "JWT_PRIVATE_KEY_PATH", default="/run/keys/jwt_private.pem"
)
JWT_PUBLIC_KEY_PATH = env(
    "JWT_PUBLIC_KEY_PATH", default="/run/keys/jwt_public.pem"
)

try:
    JWT_PRIVATE_KEY = Path(JWT_PRIVATE_KEY_PATH).read_text()
    JWT_PUBLIC_KEY = Path(JWT_PUBLIC_KEY_PATH).read_text()
except FileNotFoundError:
    JWT_PRIVATE_KEY = ""
    JWT_PUBLIC_KEY = ""

SIMPLE_JWT = {
    "ALGORITHM": "RS256",
    "SIGNING_KEY": JWT_PRIVATE_KEY,
    "VERIFYING_KEY": JWT_PUBLIC_KEY,
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

STORAGE_BACKEND = env("STORAGE_BACKEND", default="local")
STORAGE_ROOT = env("STORAGE_ROOT", default=str(BASE_DIR / "media"))

INTERNAL_TOKEN = env("INTERNAL_TOKEN", default="dev-internal-token")
AI_API_URL = env("AI_API_URL", default="http://ai_api:8000")

IMAGE_MAX_BYTES = env.int("IMAGE_MAX_BYTES", default=10 * 1024 * 1024)
IMAGE_ALLOWED_CONTENT_TYPES = env.list(
    "IMAGE_ALLOWED_CONTENT_TYPES",
    default=["image/jpeg", "image/png", "image/webp"],
)

AI_PROCESS_TIMEOUT_SECONDS = env.int("AI_PROCESS_TIMEOUT_SECONDS", default=60)
PRESIGNED_URL_TTL_SECONDS = env.int("PRESIGNED_URL_TTL_SECONDS", default=300)

LOGGING_CONFIG = None
from shared.logging import configure_logging  # noqa: E402
configure_logging()
