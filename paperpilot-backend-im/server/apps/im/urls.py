import collections.abc
import typing
from uuid import UUID

import google.protobuf
import google.protobuf.empty_pb2
import paperpilot_common.protobuf
import paperpilot_common.protobuf.im.im_pb2
from paperpilot_common.middleware.server.auth import AuthMixin
from paperpilot_common.protobuf.im import im_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext

from .services import im_service


def grpc_hook(server):
    im_pb2_grpc.add_IMServiceServicer_to_server(IMController(), server)
    im_pb2_grpc.add_IMPublicServiceServicer_to_server(
        IMPublicController(), server
    )

    return [
        _.full_name
        for _ in dict(
            paperpilot_common.protobuf.im.im_pb2.DESCRIPTOR.services_by_name
        ).values()
    ]


class IMPublicController(im_pb2_grpc.IMPublicServiceServicer, AuthMixin):
    async def IMAuth(
        self,
        request: google.protobuf.empty_pb2.Empty,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.im.im_pb2.IMAuthResponse,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.im.im_pb2.IMAuthResponse
        ],
    ]:
        return await im_service.get_im_auth(self.user.id)


class IMController(im_pb2_grpc.IMServiceServicer):
    async def CreateUser(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.CreateUserRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        await im_service.create_user(
            user_id=UUID(request.id),
            username=request.username,
        )

        return google.protobuf.empty_pb2.Empty()

    async def UpdateUser(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.UpdateUserRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        await im_service.update_user(
            user_id=UUID(request.id),
            username=request.username,
            avatar=request.avatar,
        )

        return google.protobuf.empty_pb2.Empty()

    async def CreateWorkGroup(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.CreateWorkGroupRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        await im_service.create_group(
            group_id=UUID(request.id),
            name=request.name,
            owner=request.owner,
        )

        return google.protobuf.empty_pb2.Empty()

    async def UpdateWorkGroup(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.UpdateWorkGroupRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        await im_service.update_group(
            group_id=UUID(request.id),
            name=request.name,
        )

        return google.protobuf.empty_pb2.Empty()

    async def DeleteWorkGroup(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.DeleteWorkGroupRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        await im_service.delete_group(
            group_id=UUID(request.id),
        )

        return google.protobuf.empty_pb2.Empty()

    async def InviteUserToGroup(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.InviteUserToGroupRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        await im_service.add_group_member(
            group_id=UUID(request.group_id),
            user_id=UUID(request.user_id),
        )

        return google.protobuf.empty_pb2.Empty()

    async def RemoveUserFromGroup(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.RemoveUserFromGroupRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        await im_service.delete_group_member(
            group_id=UUID(request.group_id),
            user_id=UUID(request.user_id),
        )

        return google.protobuf.empty_pb2.Empty()
