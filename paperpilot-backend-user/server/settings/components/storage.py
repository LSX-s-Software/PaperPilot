from server.settings.util import BASE_DIR, config

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
        "BACKEND": "paperpilot_common.oss.backends.OssMediaStorage",
    }
}

ALIYUN_OSS = {
    "ACCESS_KEY_ID": config("ALIYUN_OSS_ACCESS_KEY_ID", ""),
    "ACCESS_KEY_SECRET": config("ALIYUN_OSS_ACCESS_KEY_SECRET", ""),
    "ENDPOINT": "https://oss-cn-hangzhou.aliyuncs.com",
    "BUCKET_NAME": config("ALIYUN_OSS_BUCKET_NAME", ""),
    "URL_EXPIRE_SECOND": 60 * 60 * 24 * 30,
    "TOKEN_EXPIRE_SECOND": 60,
    "MAX_SIZE_MB": 100,
    "CALLBACK_BASE_URL": config("CALLBACK_BASE_URL", "http://127.0.0.1:8000"),
}

# endregion
