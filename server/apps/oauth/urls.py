import collections.abc
import typing

import google.protobuf.empty_pb2
import paperpilot_common.protobuf.user.auth_pb2
import paperpilot_common.protobuf.user.user_pb2
from paperpilot_common.exceptions import ApiException
from paperpilot_common.protobuf.user import auth_pb2_grpc
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.types import _ServicerContext

from .services import auth_service


def grpc_hook(server):
    """
    注册 grpc 服务
    """
    auth_pb2_grpc.add_AuthPublicServiceServicer_to_server(
        AuthPublicController(), server
    )


class AuthPublicController(auth_pb2_grpc.AuthPublicServiceServicer):
    """
    认证公开接口
    """

    async def Login(
        self,
        request: paperpilot_common.protobuf.user.auth_pb2.LoginRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.auth_pb2.LoginResponse,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.auth_pb2.LoginResponse
        ],
    ]:
        return await auth_service.login(request.phone, request.password)

    async def Refresh(
        self,
        request: paperpilot_common.protobuf.user.auth_pb2.RefreshTokenRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.auth_pb2.RefreshTokenResponse,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.auth_pb2.RefreshTokenResponse
        ],
    ]:
        return paperpilot_common.protobuf.user.auth_pb2.RefreshTokenResponse(
            access=await auth_service.refresh(request.refresh_token)
        )

    async def Logout(
        self,
        request: google.protobuf.empty_pb2.Empty,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        raise ApiException(ResponseType.APINotFound, detail="接口未实现")

    async def Register(
        self,
        request: paperpilot_common.protobuf.user.user_pb2.CreateUserRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.auth_pb2.LoginResponse,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.auth_pb2.LoginResponse
        ],
    ]:
        return await auth_service.register(
            phone=request.phone,
            code=request.code,
            username=request.username,
            password=request.password,
        )

    async def SendSmsCode(
        self,
        request: paperpilot_common.protobuf.user.auth_pb2.SendSmsCodeRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        await auth_service.send_sms_code(request.phone)
        return google.protobuf.empty_pb2.Empty()

    async def CountPhone(
        self,
        request: paperpilot_common.protobuf.user.auth_pb2.CountPhoneRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.auth_pb2.CountResponse,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.auth_pb2.CountResponse
        ],
    ]:
        count = await auth_service.count_phone(request.phone)
        return paperpilot_common.protobuf.user.auth_pb2.CountResponse(
            count=count
        )

    async def CountUsername(
        self,
        request: paperpilot_common.protobuf.user.auth_pb2.CountUsernameRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.auth_pb2.CountResponse,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.auth_pb2.CountResponse
        ],
    ]:
        count = await auth_service.count_username(request.username)
        return paperpilot_common.protobuf.user.auth_pb2.CountResponse(
            count=count
        )
