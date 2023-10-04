import functools

from paperpilot_common.grpc.client.cache import StubCache
from paperpilot_common.utils.log import get_logger


class StubCacheWrapper:
    cache: StubCache

    def __init__(self, stub):
        self.stub = stub
        self.stub_name = stub.__class__.__name__
        self.cache = StubCache(self.stub_name)
        self.logger = get_logger(f"grpc.client.cache_wrapper.{self.stub_name}")

    async def _call_method_and_cache(self, method, method_name, args, kwargs, use_cache, update_cache):
        """
        将grpc的方法调用转换为缓存方法调用

        :param method: grpc方法
        :param method_name: grpc方法名
        :param args: grpc方法参数
        :param kwargs: grpc方法参数
        :param use_cache: 是否使用缓存
        :param update_cache: 是否更新缓存
        :return: grpc方法返回值
        """
        if use_cache:
            # If using cache, check if the result is cached
            result = await self.cache.get_result(method_name, args, kwargs)
            if result:  # If cached, return the cached result
                self.logger.debug(f"cache hit: {method_name}")
                return result

        # If not cached, call the method and cache the result
        result = await method(*args, **kwargs)
        if update_cache:
            await self.cache.set_result(method_name, args, kwargs, result)

        return result

    def __getattr__(self, name):
        """
        将grpc的方法调用转换为缓存方法调用

        :param name: 方法名
        :return: 带缓存的方法
        """
        # Intercept any async method calls and call them through the cache
        method = getattr(self.stub, name, None)
        if method:

            @functools.wraps(method)
            async def wrapper(*args, **kwargs):
                use_cache = kwargs.pop("use_cache", False)
                update_cache = kwargs.pop("update_cache", True)
                return await self._call_method_and_cache(method, name, args, kwargs, use_cache, update_cache)

            return wrapper
        else:
            return method

    def __repr__(self):
        return f"<StubCacheWrapper {super().__repr__()}>"

    def __str__(self):
        return super().__str__
