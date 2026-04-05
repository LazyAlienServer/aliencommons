"""
This settings file is independent and not included in the base->dev/pro/staging structure.
"""

from pathlib import Path

from django.utils.translation import gettext_lazy as _


BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = "test-secret-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "core.apps.CoreConfig",
    "users.apps.UsersConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pages.apps.PagesConfig",
    "logs.apps.LogsConfig",
    "articles.apps.ArticlesConfig",
    "tasks.apps.TasksConfig",
    "corsheaders",
    "rest_framework",
    "django_filters",
    "django_rq",
    "django_tasks_rq",
    "drf_spectacular",
]

AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["users.backends.EmailBackend"]

DEFAULT_AVATARS = [
    "default_avatar/Axe.webp",
    "default_avatar/Hoe.webp",
    "default_avatar/Pickaxe.webp",
    "default_avatar/Shovel.webp",
    "default_avatar/Sword.webp",
]

SESSION_COOKIE_AGE = 1209600
SESSION_EXPIRY_REFRESH_INTERVAL = 600
SESSION_EXPIRY_REFRESH_FIELD = "last_expiry_refresh_at"

VERIFICATION_CODE_RESEND_COOLDOWN = 60
VERIFICATION_CODE_TTL = 600
MAX_VERIFICATION_ATTEMPTS = 10

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = "AlienCommons Test <noreply@test.local>"
SERVER_EMAIL = "server@test.local"

YOUTUBE_CHANNEL_ID = "test-channel-id"
YOUTUBE_CHANNEL_HANDLE = "@test-channel"
YOUTUBE_REQUEST_HEADERS = {"Referer": "http://testserver"}
YOUTUBE_API_KEY = "test-api-key"
YOUTUBE_API_URL = "https://example.com/youtube"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "EXCEPTION_HANDLER": "core.views.exception_handler.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    "DATE_FORMAT": "%Y-%m-%d",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "AlienCommons Test",
    "VERSION": "1.0.0",
}

MIDDLEWARE = [
    "core.middleware.RequestMetaMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "backend.wsgi.application"

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", _("English")),
    ("zh-hans", _("Chinese Simplified")),
]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "alien-commons-tests",
    }
}

TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",
        "QUEUES": [
            "default", "email", "maintenance"
        ],
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_URL = "http://testserver"
