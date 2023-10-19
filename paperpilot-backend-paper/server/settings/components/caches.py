# Redis
import urllib

from paperpilot_common.utils.log import get_logger

from server.settings.components.configs import CacheConfig
from server.settings.util import config

CACHES = CacheConfig.get()

logger = get_logger("settings.cache")

logger.success(
    f"Redis connect to: {urllib.parse.urlparse(CACHES['default']['LOCATION']).hostname}"
)

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# region CACHEOPS
# https://github.com/Suor/django-cacheops

if config("CACHE_URL", "").startswith("redis://"):
    CACHEOPS_REDIS = config("CACHE_URL")
    if CACHEOPS_REDIS.endswith("/"):
        CACHEOPS_REDIS = CACHEOPS_REDIS[:-1]
    CACHEOPS_REDIS = CACHEOPS_REDIS + "/9"  # 选择合适的redis编号

    CACHEOPS_DEFAULTS = {"timeout": 5}
# endregion
