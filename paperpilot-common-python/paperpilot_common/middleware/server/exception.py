import time
from typing import Any, Callable

import grpc
from google.protobuf import any_pb2
from google.rpc import code_pb2, status_pb2
from grpc_status import rpc_status

from paperpilot_common.middleware.server.base import AsyncServerMiddleware, parse_method_name
from paperpilot_common.protobuf.common.exce_pb2 import Exec
from paperpilot_common.utils.log import get_logger


class ExceptionMiddleware(AsyncServerMiddleware):
    logger = get_logger("server.interceptor.customer_top")

    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        start_time: float = time.time()
        try:
            # run grpc handler
            return await method(request_or_iterator, context)
        except Exception as e:
            self.logger.exception(e)
            detail = any_pb2.Any()
            detail.Pack(Exec(name=e.__class__.__name__, msg=str(e)))
            await context.abort_with_status(
                rpc_status.to_status(
                    status_pb2.Status(
                        code=code_pb2.RESOURCE_EXHAUSTED,
                        message=str(e),
                        details=[detail],
                    )
                )
            )
        finally:
            method_info = parse_method_name(method_name)
            self.logger.info(
                f"Got Request. method:{method_info.method}, code:{context.code()}, detail:{context.details()}, duration:{time.time() - start_time}"
            )
