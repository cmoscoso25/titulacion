"""
Django settings for configuracion project.
Sistema Ceremonia de Titulación 2026 - INACAP Sede Arica.
"""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# SEGURIDAD
# =========================

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-juex_#8$49tckwax%4e!8y-ai+#9s0rik88vhsd47!s)o8=&6n"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "cmoscoso.pythonanywhere.com",
    "controldocente.pythonanywhere.com",
    "titulacion2026.pythonanywhere.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://cmoscoso.pythonanywhere.com",
    "https://controldocente.pythonanywhere.com",
    "https://titulacion2026.pythonanywhere.com",
]


# =========================
# APLICACIONES
# =========================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "titulacion.apps.TitulacionConfig",
]


# =========================
# MIDDLEWARE
# =========================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================
# URLS / WSGI
# =========================

ROOT_URLCONF = "configuracion.urls"

WSGI_APPLICATION = "configuracion.wsgi.application"


# =========================
# TEMPLATES
# =========================

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


# =========================
# BASE DE DATOS
# =========================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# =========================
# VALIDACIÓN DE CONTRASEÑAS
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =========================
# INTERNACIONALIZACIÓN
# =========================

LANGUAGE_CODE = "es-cl"

TIME_ZONE = "America/Santiago"

USE_I18N = True

USE_TZ = True


# =========================
# ARCHIVOS ESTÁTICOS Y MEDIA
# =========================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =========================
# AUTENTICACIÓN
# =========================

LOGIN_URL = "titulacion:login"
LOGIN_REDIRECT_URL = "titulacion:inicio"
LOGOUT_REDIRECT_URL = "titulacion:login"


# =========================
# CONFIGURACIÓN GENERAL
# =========================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"