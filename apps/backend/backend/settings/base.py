# from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from pathlib import Path
from environs import Env

BASE_DIR = Path(__file__).resolve().parents[2]

env = Env()


"""Core Settings"""
ABSOLUTE_URL_OVERRIDES = {}

ADMINS = []

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

APPEND_SLASH = True

# Redis DB 0 is for django cache, Redis DB 1 is for tasks
REDIS_URL = env.str("REDIS_URL")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
        "KEY_PREFIX": env.str("REDIS_KEY_PREFIX"),
    }
}
CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_KEY_PREFIX = ""
CACHE_MIDDLEWARE_SECONDS = 600

CSRF_COOKIE_AGE = 31449600
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_PATH = "/"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = False
CSRF_USE_SESSIONS = False
CSRF_FAILURE_VIEW = "django.views.csrf.csrf_failure"
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"
CSRF_TRUSTED_ORIGINS = []

DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": False,
        "AUTO_COMMIT": True,
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("POSTGRES_HOST"),
        "NAME": env("POSTGRES_DB"),
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": False,
        "OPTIONS": {},
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "PORT": "5432",
        "TIME_ZONE": None,
        "DISABLE_SERVER_SIDE_CURSORS": False,
        "USER": env("POSTGRES_USER"),
    }
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
DATA_UPLOAD_MAX_NUMBER_FILES = 100

DATABASE_ROUTERS = []

DATE_FORMAT = "N j, Y"
DATE_INPUT_FORMATS = [
    "%Y-%m-%d",  # '2006-10-25'
    "%m/%d/%Y",  # '10/25/2006'
    "%m/%d/%y",  # '10/25/06'
    "%b %d %Y",  # 'Oct 25 2006'
    "%b %d, %Y",  # 'Oct 25, 2006'
    "%d %b %Y",  # '25 Oct 2006'
    "%d %b, %Y",  # '25 Oct, 2006'
    "%B %d %Y",  # 'October 25 2006'
    "%B %d, %Y",  # 'October 25, 2006'
    "%d %B %Y",  # '25 October 2006'
    "%d %B, %Y",  # '25 October, 2006'
]
DATETIME_FORMAT = "N j, Y, P"
DATETIME_INPUT_FORMATS = [
    "%Y-%m-%d %H:%M:%S",  # '2006-10-25 14:30:59'
    "%Y-%m-%d %H:%M:%S.%f",  # '2006-10-25 14:30:59.000200'
    "%Y-%m-%d %H:%M",  # '2006-10-25 14:30'
    "%m/%d/%Y %H:%M:%S",  # '10/25/2006 14:30:59'
    "%m/%d/%Y %H:%M:%S.%f",  # '10/25/2006 14:30:59.000200'
    "%m/%d/%Y %H:%M",  # '10/25/2006 14:30'
    "%m/%d/%y %H:%M:%S",  # '10/25/06 14:30:59'
    "%m/%d/%y %H:%M:%S.%f",  # '10/25/06 14:30:59.000200'
    "%m/%d/%y %H:%M",  # '10/25/06 14:30'
]

DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = False

DECIMAL_SEPARATOR = "."

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_CHARSET = "utf-8"
DEFAULT_EXCEPTION_REPORTER = "django.views.debug.ExceptionReporter"
DEFAULT_EXCEPTION_REPORTER_FILTER = "django.views.debug.SafeExceptionReporterFilter"
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")
DEFAULT_INDEX_TABLESPACE = ""
DEFAULT_TABLESPACE = ""

DISALLOWED_USER_AGENTS = []

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_SUBJECT_PREFIX = "[Django]"
EMAIL_USE_LOCALTIME = False
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL")
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = None

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440
FILE_UPLOAD_DIRECTORY_PERMISSIONS = None
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_TEMP_DIR = None

FIRST_DAY_OF_WEEK = 0

FIXTURE_DIRS = []

FORCE_SCRIPT_NAME = None

FORM_RENDERER = None

FORMAT_MODULE_PATH = None

IGNORABLE_404_URLS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
    "users.apps.UsersConfig",
    "pages.apps.PagesConfig",
    "logs.apps.LogsConfig",
    "articles.apps.ArticlesConfig",
    "tasks.apps.TasksConfig",
    "corsheaders",
    "rest_framework",
    "django_filters",
    "django_rq",
    "django_tasks_rq",
]

INTERNAL_IPS = []

# LANGUAGE_CODE = "en-us"
LANGUAGE_COOKIE_AGE = None
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_COOKIE_PATH = "/"
LANGUAGE_COOKIE_SAMESITE = None
LANGUAGE_COOKIE_SECURE = False
# LANGUAGES = [
#     ("en_us", _("English")),
#     ("zh-hans", _("Chinese Simplified"))
# ]

LOCALE_PATHS = []

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "runtime": {
            "()": "logs.logging.formatters.RuntimeFormatter",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "runtime",
            "level": "INFO",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
LOGGING_CONFIG = "logging.config.dictConfig"

MANAGERS = []

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

MIDDLEWARE = [
    "core.middleware.RequestMetaMiddleware",
    "logs.middleware.RequestLoggingMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "users.middleware.SessionTrackingMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

MIGRATION_MODULES = {}

MONTH_DAY_FORMAT = "F j"

NUMBER_GROUPING = 0

PREPEND_WWW = False

ROOT_URLCONF = "backend.urls"

SECRET_KEY = env.str("SECRET_KEY")
SECRET_KEY_FALLBACKS = []

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SECURE_CSP = {}
SECURE_CSP_REPORT_ONLY = {}
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_HSTS_SECONDS = 0
SECURE_PROXY_SSL_HEADER = None
SECURE_REDIRECT_EXEMPT = []
SECURE_REFERRER_POLICY = "same-origin"
SECURE_SSL_HOST = None
SECURE_SSL_REDIRECT = False

SERVER_EMAIL = env.str("SERVER_EMAIL")

SHORT_DATE_FORMAT = "m/d/Y"
SHORT_DATETIME_FORMAT = "m/d/Y P"

SIGNING_BACKEND = "django.core.signing.TimestampSigner"

SILENCED_SYSTEM_CHECKS = []

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

TASKS = {
    "default": {
        "BACKEND": "django_tasks_rq.backend.RQBackend",
        "QUEUES": [
            "default", "email", "maintenance"
        ],
        "OPTIONS": {}
    }
}

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

TEST_RUNNER = "django.test.runner.DiscoverRunner"
TEST_NON_SERIALIZED_APPS = []

THOUSAND_SEPARATOR = ","

TIME_FORMAT = "P"
TIME_INPUT_FORMATS = [
    "%H:%M:%S",  # '14:30:59'
    "%H:%M:%S.%f",  # '14:30:59.000200'
    "%H:%M",  # '14:30'
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_THOUSAND_SEPARATOR = False

USE_TZ = True

USE_X_FORWARDED_HOST = False
USE_X_FORWARDED_PORT = False

WSGI_APPLICATION = "backend.wsgi.application"

YEAR_MONTH_FORMAT = "F Y"

X_FRAME_OPTIONS = "DENY"


"""Auth Settings"""
AUTHENTICATION_BACKENDS = ["users.backends.EmailBackend"]

AUTH_USER_MODEL = "users.User"

# The following values are set to 'None' because this backend is api-only
LOGIN_REDIRECT_URL = None
LOGIN_URL = None
LOGOUT_REDIRECT_URL = None
PASSWORD_RESET_TIMEOUT = 259200

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator", },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]


"""Messages Settings"""
MESSAGE_LEVEL = messages.INFO
MESSAGE_STORAGE = "django.contrib.messages.storage.fallback.FallbackStorage"
MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "error",
}


"""Sessions Settings"""
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_PATH = "/"
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_FILE_PATH = None
SESSION_SAVE_EVERY_REQUEST = False
SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"


"""Sites Settings"""
SITE_URL = env.str("SITE_URL")


"""Static Files Settings"""
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


"""Third-Party Package Settings"""
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    "DEFAULT_PARSER_CLASSES": [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_CONTENT_NEGOTIATION_CLASS": "rest_framework.negotiation.DefaultContentNegotiation",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",

    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardPagination",
    "PAGE_SIZE": 20,

    "EXCEPTION_HANDLER": "core.views.exception_handler.custom_exception_handler",
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    "DATE_FORMAT": "%Y-%m-%d",
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

SPECTACULAR_SETTINGS = {
    'TITLE': 'AlienCommons',
    'VERSION': '1.0.0',
}

RQ_QUEUES = {
    "default": {
        "URL": f"{REDIS_URL}/0",
        "DEFAULT_TIMEOUT": 300,
    },
    "email": {
        "URL": f"{REDIS_URL}/0",
        "DEFAULT_TIMEOUT": 300,
    },
    "maintenance": {
        "URL": f"{REDIS_URL}/0",
        "DEFAULT_TIMEOUT": 300,
    },
}

"""Custom Settings"""
DEFAULT_AVATARS = [
    'default_avatar/Axe.webp',
    'default_avatar/Hoe.webp',
    'default_avatar/Pickaxe.webp',
    'default_avatar/Shovel.webp',
    'default_avatar/Sword.webp',
]

SESSION_EXPIRY_REFRESH_INTERVAL = 600
SESSION_EXPIRY_REFRESH_FIELD = 'last_expiry_refresh_at'

VERIFICATION_CODE_RESEND_COOLDOWN = 60
VERIFICATION_CODE_TTL = 600
MAX_VERIFICATION_ATTEMPTS = 10

YOUTUBE_CHANNEL_ID = env.str("YOUTUBE_CHANNEL_ID")
YOUTUBE_CHANNEL_HANDLE = env.str("YOUTUBE_CHANNEL_HANDLE")
YOUTUBE_REQUEST_HEADERS = {
    "Referer": "http://localhost:8000",
}
YOUTUBE_API_KEY = env.str("YOUTUBE_API_KEY")
YOUTUBE_API_URL = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"
