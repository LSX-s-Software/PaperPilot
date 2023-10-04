import uuid
from contextvars import ContextVar
from typing import Any, Callable

import grpc
from django.conf import settings

from paperpilot_common.middleware.server.base import AsyncServerMiddleware
from paperpilot_common.utils.log import get_logger


class UserContext:
    """
    用户上下文
    """

    id: uuid.UUID | None = None

    def __init__(self, user_id: str | None = None):
        if user_id:
            self.id = uuid.UUID(user_id)
        else:
            self.id = None

    @property
    def is_anonymous(self) -> bool:
        return self.id is None

    @property
    def is_authenticated(self) -> bool:
        return self.id is not None

    def __repr__(self) -> str:
        return f"<UserContext user_id={self.id}>"


user_context: ContextVar[UserContext | None] = ContextVar("user_context", default=None)


def get_user() -> UserContext:
    user = user_context.get()
    if user is None:
        user_context.set(UserContext())

    return user_context.get()


class AuthMixin:
    @property
    def user(self) -> UserContext:
        return get_user()


class AuthMiddleware(AsyncServerMiddleware):
    logger = get_logger("server.interceptor.auth")
    auth_metadata_key: str = getattr(settings, "AUTH_METADATA_KEY", "x-kong-jwt-claim-user_id")

    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        try:
            metadata = dict(context.invocation_metadata())
            user_id = metadata.get(self.auth_metadata_key, None)
            user_context.set(UserContext(user_id))

            return await method(request_or_iterator, context)
        except Exception as e:
            self.logger.exception(e)
            raise e
