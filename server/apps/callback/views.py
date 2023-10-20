import abc
from urllib.parse import parse_qs
from uuid import UUID

import pytz
from paperpilot_common.exceptions import ApiException
from paperpilot_common.middleware.server.context import trace_id_context
from paperpilot_common.oss.callback import OssCallbackChecker
from paperpilot_common.protobuf.user.user_pb2 import (
    UpdateUserAvatarRequest,
    UserDetail,
)
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from server.business.grpc.user import user_client


class BaseCallbackView(HTTPEndpoint):
    logger_name = "callback.base_view"
    checker = OssCallbackChecker()

    def __init__(self, *args, **kwargs):
        self.logger = get_logger(self.logger_name)
        super().__init__(*args, **kwargs)

    async def post(self, request):
        self.logger.debug(f"callback, request: {request}")

        query_string = "&".join(
            [f"{k}={v}" for k, v in request.query_params.items()]
        )

        if not await self.checker.check_callback_signature(
            headers=request.headers,
            body=await request.body(),
            query_string=query_string,
            path_info=request.url.path,
        ):
            raise ApiException(
                ResponseType.PermissionDenied, "OSS回调签名检验失败", record=True
            )

        query = dict(request.query_params)
        body = {
            k.decode(): v[0].decode()
            for k, v in parse_qs(await request.body()).items()
        }

        trace_id = UUID(body["trace_id"])
        trace_id_context.set(trace_id)

        return await self.handle(query, body, request)

    @abc.abstractmethod
    async def handle(
        self, query: dict[str, str], body: dict[str, str], request: Request
    ) -> JSONResponse:
        """
        处理回调

        :param query: query参数
        :param body: body参数
        :param request: 请求对象
        :return: JSON响应
        """
        raise NotImplementedError


class CallbackUserAvatarView(BaseCallbackView):
    logger_name = "callback.user.avatar.view"
    user_service = user_client.stub

    async def handle(
        self, query: dict[str, str], body: dict[str, str], request: Request
    ) -> JSONResponse:
        user_id = query.get("user_id", None)
        if user_id is None:
            raise ApiException(
                ResponseType.ParamEmpty, "user_id不能为空", record=True
            )

        key = body.get("object", None)
        if key is None:
            raise ApiException(
                ResponseType.ParamEmpty, "object不能为空", record=True
            )

        self.logger.debug(
            f"callback update user avatar, user_id: {user_id}, object: {key}"
        )

        user_detail: UserDetail = await self.user_service.UpdateUserAvatar(
            UpdateUserAvatarRequest(
                id=user_id,
                avatar=key,
            )
        )

        return JSONResponse(
            {
                "id": user_detail.id,
                "username": user_detail.username,
                "phone": user_detail.phone,
                "avatar": user_detail.avatar,
                "create_time": user_detail.create_time.ToDatetime(
                    tzinfo=pytz.utc
                )
                .astimezone()
                .isoformat(),
                "update_time": user_detail.create_time.ToDatetime(
                    tzinfo=pytz.utc
                )
                .astimezone()
                .isoformat(),
            }
        )
