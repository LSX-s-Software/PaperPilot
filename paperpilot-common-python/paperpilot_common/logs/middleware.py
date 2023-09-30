import asyncio
import time

from paperpilot_common.logs.threads import LOGGER_THREAD
from paperpilot_common.logs.utils import database_log_enabled


class APILoggerMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        self._is_coroutine = asyncio.iscoroutinefunction(get_response)

    def __call__(self, request):
        if not database_log_enabled():
            return self.get_response(request)

        if self._is_coroutine:
            return self.insert_log_async(request)
        else:
            return self.insert_log(request)

    def insert_log(self, request):
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()
        LOGGER_THREAD.put_log_data(request, response, start_time, end_time)

        return response

    async def insert_log_async(self, request):
        start_time = time.time()
        response = await self.get_response(request)
        end_time = time.time()
        LOGGER_THREAD.put_log_data(request, response, start_time, end_time)

        return response
