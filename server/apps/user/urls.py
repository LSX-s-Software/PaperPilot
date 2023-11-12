import collections.abc
import typing
import uuid

import google.protobuf
import google.protobuf.empty_pb2
import paperpilot_common.protobuf
import paperpilot_common.protobuf.user.user_pb2
from paperpilot_common.middleware.server.auth import AuthMixin
from paperpilot_common.oss.direct import generate_direct_upload_token
from paperpilot_common.oss.utils import get_random_name
from paperpilot_common.protobuf.user import user_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext

from .models import User
from .services import user_service


def grpc_hook(server):
    user_pb2_grpc.add_UserServiceServicer_to_server(UserController(), server)
    user_pb2_grpc.add_UserPublicServiceServicer_to_server(
        UserPublicController(), server
    )

    return [
        _.full_name
        for _ in dict(
            paperpilot_common.protobuf.user.user_pb2.DESCRIPTOR.services_by_name
        ).values()
    ]


class UserPublicController(user_pb2_grpc.UserPublicServiceServicer, AuthMixin):
    async def GetUserInfo(
        self,
        request: paperpilot_common.protobuf.user.user_pb2.UserId,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.user_pb2.UserInfo,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.user_pb2.UserInfo
        ],
    ]:
        return await user_service.get_user_info(request.id)

    async def GetCurrentUser(
        self,
        request: google.protobuf.empty_pb2.Empty,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.user_pb2.UserDetail,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.user_pb2.UserDetail
        ],
    ]:
        return await user_service.get_user_detail(self.user.id)

    async def UpdateUser(
        self,
        request: paperpilot_common.protobuf.user.user_pb2.UpdateUserRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.user_pb2.UserDetail,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.user_pb2.UserDetail
        ],
    ]:
        return await user_service.update_user(self.user.id, request)

    async def UploadUserAvatar(
        self,
        request: google.protobuf.empty_pb2.Empty,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.user_pb2.UploadUserAvatarResponse,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.user_pb2.UploadUserAvatarResponse
        ],
    ]:
        token = generate_direct_upload_token(
            callback_url=f"callback/user/avatar/?user_id={self.user.id.hex}",
            content_type=["image/jpeg"],
            key=f"{User.AVATAR_PATH}/{get_random_name('.jpg')}",
            min_size="1kb",
            max_size="1mb",
            # callback_body="object=${object}",
        )
        return (
            paperpilot_common.protobuf.user.user_pb2.UploadUserAvatarResponse(
                token=token.to_protobuf()
            )
        )


class UserController(user_pb2_grpc.UserServiceServicer):
    async def GetUserInfo(
        self,
        request: paperpilot_common.protobuf.user.user_pb2.UserId,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.user_pb2.UserInfo,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.user_pb2.UserInfo
        ],
    ]:
        return await user_service.get_user_info(request.id)

    async def GetUserDetail(
        self,
        request: paperpilot_common.protobuf.user.user_pb2.UserId,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.user_pb2.UserDetail,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.user_pb2.UserDetail
        ],
    ]:
        return await user_service.get_user_detail(request.id)

    async def GetUserInfos(
        self,
        request: paperpilot_common.protobuf.user.user_pb2.UserIdList,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.user_pb2.UserInfoMap,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.user_pb2.UserInfoMap
        ],
    ]:
        infos = await user_service.get_user_infos(
            [uuid.UUID(_) for _ in request.ids]
        )
        response = paperpilot_common.protobuf.user.user_pb2.UserInfoMap(
            infos=infos,
        )
        return response

    async def UpdateUserAvatar(
        self,
        request: paperpilot_common.protobuf.user.user_pb2.UpdateUserAvatarRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.user.user_pb2.UserDetail,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.user.user_pb2.UserDetail
        ],
    ]:
        return await user_service.update_user_avatar(request.id, request.avatar)
