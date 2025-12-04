import os
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security ---
SECRET_KEY = "change-this-in-production-very-secret"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# --- Applications ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.humanize',
    "shop",
]

# --- Middleware ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --- URLs & WSGI ---
ROOT_URLCONF = "django_shop.urls"
WSGI_APPLICATION = "django_shop.wsgi.application"

# --- Templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "shop" / "templates"],
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

# --- Database ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalization ---
LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Almaty"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('kk', 'Қазақ'),
    ('ru', 'Русский'),
    ('en', 'English'),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

# --- Static & Media ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "shop" / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Login URLs ---
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# === Authentication backends (Django + OIDC) ===
AUTHENTICATION_BACKENDS = [
    "shop.oidc_backend.KeycloakOIDCBackend",  # Keycloak OIDC
    "django.contrib.auth.backends.ModelBackend",  # стандартная авторизация Django
]

# === Keycloak / OIDC settings ===
OIDC_RP_CLIENT_ID = "dev-api"
OIDC_RP_CLIENT_SECRET = "IYNTgfddrkcyjbdSwCk6PujRsRiDS9cG"
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
OIDC_RP_CALLBACK_URL = "http://localhost:8000/oidc/callback/"

OIDC_OP_DISCOVERY_DOCUMENT_URL = "https://idp.nic.kz:8443/realms/dev-nic/.well-known/openid-configuration"
OIDC_OP_AUTHORIZATION_ENDPOINT = "https://idp.nic.kz:8443/realms/dev-nic/protocol/openid-connect/auth"
OIDC_OP_TOKEN_ENDPOINT = "https://idp.nic.kz:8443/realms/dev-nic/protocol/openid-connect/token"
OIDC_OP_USER_ENDPOINT = "https://idp.nic.kz:8443/realms/dev-nic/protocol/openid-connect/userinfo"
OIDC_OP_JWKS_ENDPOINT = "https://idp.nic.kz:8443/realms/dev-nic/protocol/openid-connect/certs"
OIDC_OP_LOGOUT_ENDPOINT = "https://idp.nic.kz:8443/realms/dev-nic/protocol/openid-connect/logout"

OIDC_RP_SIGN_ALGO = "RS256"
OIDC_RP_IDP_SIGN_ALG = "RS256"
OIDC_USE_NONCE = True
OIDC_RENEW_ID_TOKEN_BEFORE_EXPIRY = True
OIDC_AUTH_REQUEST_SCOPES = ["openid", "profile", "email"]
OIDC_CREATE_USER = True
OIDC_STORE_ACCESS_TOKEN = True
OIDC_STORE_ID_TOKEN = True
OIDC_VERIFY_SSL = False  # True для продакшена
SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "APP": {
            "client_id": "...",
            "secret": "...",
            "server_url": "https://idp.nic.kz:8443/realms/dev-nic",
        },
        "OAUTH_PKCE_ENABLED": True,
        "AUTH_PARAMS": {"prompt": "login"},
    }
}

