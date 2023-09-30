from contextvars import ContextVar
from typing import Any, Callable

import grpc

from paperpilot_common.middleware.server.base import AsyncServerMiddleware
from paperpilot_common.utils.log import get_logger


class UserContext:
    """
    用户上下文
    """

    user_id: str | None = None

    def __init__(self, user_id: str | None = None):
        self.user_id = user_id

    @property
    def is_anonymous(self) -> bool:
        return self.user_id is None

    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None

    def __repr__(self) -> str:
        return f"<UserContext user_id={self.user_id}>"


user_context: ContextVar[UserContext | None] = ContextVar("user_context", default=None)


class AuthMiddleware(AsyncServerMiddleware):
    logger = get_logger("server.interceptor.auth")
    auth_metadata_key: str = "x-kong-jwt-claim-name"

    def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        try:
            metadata = self.metadata_dict
            user_id = metadata.get(self.auth_metadata_key)

            if user_context.get() is None:
                user_context.set(UserContext(user_id))

            return method(request_or_iterator, context)
        except Exception as e:
            self.logger.exception(e)
            raise e
