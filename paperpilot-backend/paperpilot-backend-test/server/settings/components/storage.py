from server.settings.util import BASE_DIR

# region Static files
# https://docs.djangoproject.com/en/2.2/howto/static-files

STATIC_URL = "https://zq-public-oss.oss-cn-hangzhou.aliyuncs.com/zq-auth/backend/static/static/"

STATIC_ROOT = str(BASE_DIR.joinpath("static"))
# endregion

# region 媒体文件
MEDIA_URL = "/"
# endregion

# region oss
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    }
}

# endregion
