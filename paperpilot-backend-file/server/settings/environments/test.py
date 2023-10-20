DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "async_default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
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

SENTRY_ENABLE = False
