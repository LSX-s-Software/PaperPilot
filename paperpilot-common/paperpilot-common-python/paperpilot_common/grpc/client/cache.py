import hashlib

from paperpilot_common.utils.cache import Cache


class StubCache(Cache):
    logger_name = "grpc.client.cache"
    default_timeout = 5

    def __init__(self, stub_name: str):
        self.stub_name = stub_name
        self.logger_name = f"{self.logger_name}.{stub_name}"
        super().__init__()

    def _generate_cache_key(self, method, args, kwargs):
        # Generate a unique cache key based on method name, args, and kwargs
        key = f"{self.stub_name}:{method}:{self._calculate_hash(args, kwargs)}"
        return key

    def _calculate_hash(self, args, kwargs):
        # Calculate a hash of the args and kwargs to create a shorter cache key
        data = str((args, kwargs)).encode("utf-8")
        return hashlib.sha512(data).hexdigest()

    async def get_result(self, method, args, kwargs):
        cache_key = self._generate_cache_key(method, args, kwargs)
        return await self.get_async(cache_key)

    async def set_result(self, method, args, kwargs, result):
        cache_key = self._generate_cache_key(method, args, kwargs)
        await self.set_async(cache_key, result, timeout=self.default_timeout)

    async def delete_result(self, method, args, kwargs):
        cache_key = self._generate_cache_key(method, args, kwargs)
        await self.delete_async(cache_key)
