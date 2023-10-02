from server.settings import ZQ_EXCEPTION

DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

SECRET_KEY = "not very secret in tests"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": True,  # We want template errors to raise
        },
    },
]

ZQ_EXCEPTION["EXCEPTION_UNKNOWN_HANDLE"] = False

SENTRY_ENABLE = False

DRF_LOGGER = {
    "DEFAULT_DATABASE": "default",
    "QUEUE_MAX_SIZE": 50,
    "INTERVAL": 10,
    "DATABASE": False,
    "SIGNAL": False,
    "PATH_TYPE": "FULL_PATH",
    "SKIP_URL_NAME": [],
    "SKIP_NAMESPACE": [],
    "METHODS": None,
    "STATUS_CODES": None,
    "SENSITIVE_KEYS": [],
    "ADMIN_SLOW_API_ABOVE": 500,
    "ADMIN_TIMEDELTA": 0,
}

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
