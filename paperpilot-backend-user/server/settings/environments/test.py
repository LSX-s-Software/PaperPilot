from server.settings.components.configs import DatabaseConfig

DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = True

DATABASES = DatabaseConfig.get(
    "mysql://paperpilot:paperpilot@localhost:3306/paperpilot"
)


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

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "LOCATION": "/tmp",
    }
}

ALIYUN_OSS = {
    "ACCESS_KEY_ID": "key_id",
    "ACCESS_KEY_SECRET": "key_secret",
    "ENDPOINT": "https://oss-cn-hangzhou.aliyuncs.com",
    "BUCKET_NAME": "bucket_name",
    "URL_EXPIRE_SECOND": 60 * 60 * 24 * 30,
    "TOKEN_EXPIRE_SECOND": 60,
    "MAX_SIZE_MB": 100,
    "CALLBACK_BASE_URL": "http://localhost:8000",
}
