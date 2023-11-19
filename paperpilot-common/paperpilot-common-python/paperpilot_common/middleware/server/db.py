from typing import Any, Callable

import grpc

from paperpilot_common.middleware.server.base import AsyncServerMiddleware, parse_method_name
from paperpilot_common.utils.db import close_old_connections
from paperpilot_common.utils.log import get_logger


class DBMiddleware(AsyncServerMiddleware):
    logger = get_logger("server.interceptor.db")

    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        close_old_connections()
        result = await self.call(method, request_or_iterator, context)
        close_old_connections()
        return result
        
