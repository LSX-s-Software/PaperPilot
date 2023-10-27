import time
import uuid
from typing import Any, Callable
from uuid import UUID

import grpc
from grpc_status import rpc_status

from paperpilot_common.exceptions.handler import ApiExceptionHandler
from paperpilot_common.middleware.server.base import AsyncServerMiddleware, parse_method_name
from paperpilot_common.middleware.server.context import get_trace_id, trace_id_context
from paperpilot_common.utils.log import get_logger


class TraceMiddleware(AsyncServerMiddleware):
    logger = get_logger("server.interceptor.trace")
    handler = ApiExceptionHandler()

    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        start_time: float = time.time()

        # 获取request trace id
        trace_id = dict(context.invocation_metadata()).get("x-trace-id", None)
        if trace_id:
            trace_id_context.set(UUID(trace_id))
        else:
            trace_id_context.set(uuid.uuid4())

        try:
            # run grpc handler
            response = await self.call(method, request_or_iterator, context)
            # add trace_id to metadata
            context.set_trailing_metadata((("x-trace-id", trace_id_context.get().hex),))
            return response
        except Exception as e:
            status = self.handler.grpc_handle(e)
            await context.abort_with_status(rpc_status.to_status(status))
        finally:
            method_info = parse_method_name(method_name)
            if method_info.method not in ["ServerReflectionInfo", "Check", "Watch"]:
                self.logger.debug(
                    f"Got Request {get_trace_id()}. method:{method_info.method}, code:{context.code()}, detail:{context.details()}, duration:{time.time() - start_time}"
                )
