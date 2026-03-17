from django.utils.translation import gettext_lazy as _

from datetime import timedelta
from pathlib import Path
from environs import Env
from corsheaders.defaults import default_headers

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env.str("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
]

INSTALLED_APPS = [
    # ASGI Server
    "daphne",
    # Core
    "core.apps.CoreConfig",
    # User App
    "users.apps.UsersConfig",
    # Django Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local Apps
    "pages.apps.PagesConfig",
    "logs.apps.LogsConfig",
    "articles.apps.ArticlesConfig",
    # 3rd-party Apps
    "corsheaders",
    "rest_framework",
    "django_celery_beat",
    "django_filters",
    'drf_spectacular',
]

AUTH_USER_MODEL = "users.User"

# Custom setting - default user avatars
DEFAULT_AVATARS = [
    'default_avatar/Axe.webp',
    'default_avatar/Hoe.webp',
    'default_avatar/Pickaxe.webp',
    'default_avatar/Shovel.webp',
    'default_avatar/Sword.webp',
]

# Custom setting - verification code
VERIFICATION_CODE_RESEND_COOLDOWN = 60
VERIFICATION_CODE_TTL = 600
MAX_VERIFICATION_ATTEMPTS = 10

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = env.str("SERVER_EMAIL")
EMAIL_HOST = env.str("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL")

YOUTUBE_CHANNEL_ID = env.str("YOUTUBE_CHANNEL_ID")
YOUTUBE_CHANNEL_HANDLE = env.str("YOUTUBE_CHANNEL_HANDLE")
YOUTUBE_REQUEST_HEADERS = {
    "Referer": "http://localhost:8000",
}
YOUTUBE_API_KEY = env.str("YOUTUBE_API_KEY")
YOUTUBE_API_URL = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],

    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],

    "EXCEPTION_HANDLER": "core.views.exception_handler.custom_exception_handler",

    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardPagination",
    "PAGE_SIZE": 20,

    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    "DATE_FORMAT": "%Y-%m-%d",

    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'AlienCommons',
    'VERSION': '1.0.0',
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("ACCESS_TOKEN_LIFETIME", 10)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("REFRESH_TOKEN_LIFETIME", 60)),
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
        "DIRS": [BASE_DIR / 'templates']
        ,
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


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator", },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]


TIME_ZONE = "UTC"
USE_TZ = True

USE_I18N = True
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", _("English")),
    ("zh-hans", _("Chinese Simplified"))
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": "db",
        "PORT": "5432",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env.str("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
        "KEY_PREFIX": env.str("REDIS_KEY_PREFIX"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_URL = env.str("SITE_URL")

CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

DEFAULT_FROM_EMAIL = "noreply@aliencommons.com"
