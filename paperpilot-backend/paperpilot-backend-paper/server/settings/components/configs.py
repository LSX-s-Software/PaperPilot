import os
from copy import deepcopy
from string import Template
from typing import Any, Dict, Optional, Union

import dj_database_url
import django_cache_url

from server.settings.util import BASE_DIR, config


class DatabaseConfig:
    url = "sqlite:///" + os.path.join(BASE_DIR, "db.sqlite3")

    DATABASES = {  # {数据库名: 额外配置}
        "default": {
            "OPTIONS": {"charset": "utf8mb4"},
            "CONN_MAX_AGE": 60 * 60,
            "CONN_HEALTH_CHECKS": True,
        }
    }

    @classmethod
    def get(
        cls, url: Optional[str] = None
    ) -> Dict[str, Dict[str, Union[str, int, Dict[str, str]]]]:
        if url is None:
            url = config("DATABASE_URL", cls.url)

        res = dj_database_url.parse(url)

        if url.startswith("sqlite"):
            return {k: {**res} for k, v in cls.DATABASES.items()}

        return {k: {**v, **res} for k, v in cls.DATABASES.items()}


class CacheConfig:
    url: str = "locmem://"

    CACHES: dict[str, int] = {  # {Cache名称: 编号}
        "default": 0,
        "async_default": 0,
        "third_session": 1,  # 第三方登录缓存
        "db_cache": 2,  # 数据库缓存
    }

    @staticmethod
    def parse_url(
        url: str, db: int = 0, name: str = "default"
    ) -> Dict[str, Any]:
        cache_url = url
        if cache_url.endswith("/"):
            cache_url += f"{db}"
        else:
            cache_url += f"/{db}"

        config = django_cache_url.parse(cache_url)

        if name.startswith("async_"):
            config["BACKEND"] = "django_async_redis.cache.RedisCache"
            config["OPTIONS"] = {
                "CLIENT_CLASS": "django_async_redis.client.DefaultClient"
            }

        return config

    @classmethod
    def get(cls, url: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        if url is None:
            url = config("CACHE_URL", cls.url)

        return {
            k: {**(cls.parse_url(url, v, k))} for k, v in cls.CACHES.items()
        }


class LogConfig:
    level: str = config("LOG_LEVEL", "INFO")
    logger_level: Dict[str, str] = {}

    LOG_ROOT = BASE_DIR.joinpath("logs", "django")

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] "
                "[%(levelname)s]- %(message)s"
            },
            "simple": {"format": "%(levelname)s %(message)s"},  # 简单格式
        },
        "handlers": {
            "server": {
                "class": "server.utils.logging_handler.InterceptTimedRotatingFileHandler",
                "filename": LOG_ROOT.joinpath("server", "django.log"),
                "when": "D",
                "interval": 1,
                "backupCount": 1,
                "formatter": "standard",
                "encoding": "utf-8",
            },
            "db": {
                "class": "server.utils.logging_handler.InterceptTimedRotatingFileHandler",
                "filename": LOG_ROOT.joinpath("db", "db.log"),
                "when": "D",
                "interval": 1,
                "backupCount": 1,
                "formatter": "standard",
                "encoding": "utf-8",
                "logging_levels": [
                    "debug"
                ],  # 注意这里，这是自定义类多了一个参数，因为我只想让db日志有debug文件，所以我只看sql，这个可以自己设置
            },
            "debug": {
                "class": "server.utils.logging_handler.InterceptTimedRotatingFileHandler",
                "filename": LOG_ROOT.joinpath("debug", "debug.log"),
                "when": "D",
                "interval": 1,
                "backupCount": 1,
                "formatter": "standard",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            # Django全局绑定
            "django": {
                "handlers": ["server"],
                "propagate": True,
                "level": "${level}",
            },
            "celery": {
                "handlers": ["server"],
                "propagate": False,
                "level": "${level}",
            },
            "django.db.backends": {
                "handlers": ["db"],
                "propagate": False,
                "level": "${level}",
            },
            "django.request": {
                "handlers": ["server"],
                "propagate": False,
                "level": "${level}",
            },
            # Werkzeug Debug
            "werkzeug": {
                "handlers": ["debug"],
                "propagate": False,
                "level": "${level}",
            },
        },
    }

    @classmethod
    def get_config(cls) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(cls.LOG_ROOT):
            os.makedirs(cls.LOG_ROOT)

        res = deepcopy(cls.LOGGING)

        for logger in res["loggers"]:
            if logger in cls.logger_level:
                res["loggers"][logger]["level"] = Template(
                    res["loggers"][logger]["level"]
                ).substitute(level=cls.logger_level[logger])
            else:
                name = f"LOG_LEVEL_{logger}"
                res["loggers"][logger]["level"] = Template(
                    res["loggers"][logger]["level"]
                ).substitute(level=config(name, cls.level))

        return res
