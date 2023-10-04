from server.settings.components import config
from server.settings.components.configs import CacheConfig

# debug 模式
DEBUG = config("DJANGO_DEBUG", False, cast=bool)

ALLOWED_HOSTS = [
    "localhost",
    "teamup.ziqiang.net.cn",
    "api.teamup.ziqiang.net.cn",
    "test.teamup.ziqiang.net.cn",
    "api.test.teamup.ziqiang.net.cn",
]

SERVER_URL = config("SERVER_URL", "https://api.teamup.ziqiang.net.cn")

# region Cache
# Redis
CacheConfig.url = "redis://redis"
CACHES = CacheConfig.get()
CELERY_BROKER_URL = "redis://redis/0"
# endregion
