from typing import Any

from django.conf import settings
from django.core.cache import caches

from paperpilot_common.utils.log import get_logger


class Cache:
    base_key_name: str = settings.SERVER_NAME
    cache_name: str = "default"
    logger_name: str = "cache"
    default_timeout: int | None = None

    def __init__(self):
        self.cache = caches[self.cache_name]
        self.async_cache = caches[f"async_{self.cache_name}"]
        self.logger = get_logger(self.logger_name)

        self.logger.debug(f"cache: '{self.cache_name}' init")

    def key(self, key: str) -> str:
        return f"{self.base_key_name}:{key}"

    def get(self, key: str, default=None) -> Any:
        result = self.cache.get(self.key(key), default)
        self.logger.debug(f"get key: {self.key(key)}, result: {result}")
        return result

    def set(self, key: str, value: Any, timeout: int = default_timeout) -> None:
        self.logger.debug(f"set key: {self.key(key)}, value: {value}, timeout: {timeout}")
        self.cache.set(self.key(key), value, timeout)

    def delete(self, key: str) -> None:
        self.logger.debug(f"delete key: {self.key(key)}")
        self.cache.delete(self.key(key))

    async def get_async(self, key: str, default=None) -> Any:
        result = await self.async_cache.aget(self.key(key), default)
        self.logger.debug(f"async get key: {self.key(key)}, result: {result}")
        return result

    async def set_async(self, key: str, value: Any, timeout: int = default_timeout) -> None:
        self.logger.debug(f"async set key: {self.key(key)}, value: {value}, timeout: {timeout}")
        await self.async_cache.aset(key=self.key(key), value=value, timeout=timeout)

    async def delete_async(self, key: str) -> None:
        self.logger.debug(f"async delete key: {self.key(key)}")
        await self.async_cache.adelete(self.key(key))
