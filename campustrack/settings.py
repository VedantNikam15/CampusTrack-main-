import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------------------
# AUTO-SWITCH between LOCAL and RENDER
# ----------------------------------------------------
IS_RENDER = os.environ.get("RENDER") is not None

DEBUG = not IS_RENDER     # Local = True, Render = False

SECRET_KEY = os.environ.get("SECRET_KEY", "local-secret-key")

ALLOWED_HOSTS = ["*"]

# ----------------------------------------------------
# Applications
# ----------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "crispy_forms",
    "crispy_bootstrap5",

    "core",
]

# ----------------------------------------------------
# Middleware  (WhiteNoise ALWAYS included)
# ----------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # FIX: Always include
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "campustrack.urls"

# ----------------------------------------------------
# Templates
# ----------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "campustrack.wsgi.application"

# ----------------------------------------------------
# DATABASE (SQLite local + Render persistent disk)
# ----------------------------------------------------
if IS_RENDER:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "/var/data/db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ----------------------------------------------------
# Password Validators
# ----------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------
# STATIC FILES (Render + Local)
# ----------------------------------------------------
STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"   # MUST ALWAYS EXIST

if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise storage only on Render
if IS_RENDER:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ----------------------------------------------------
# Authentication
# ----------------------------------------------------
AUTH_USER_MODEL = "core.User"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

AUTHENTICATION_BACKENDS = [
    "core.backends.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ----------------------------------------------------
# Crispy Forms
# ----------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ----------------------------------------------------
# Email
# ----------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "CampusTrack <no-reply@campus.com>"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
