"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import abc
import collections.abc
import google.protobuf.empty_pb2
import grpc
import grpc.aio
import paperpilot_common.protobuf.im.im_pb2
import typing

_T = typing.TypeVar("_T")

class _MaybeAsyncIterator(collections.abc.AsyncIterator[_T], collections.abc.Iterator[_T], metaclass=abc.ABCMeta): ...

class _ServicerContext(grpc.ServicerContext, grpc.aio.ServicerContext):  # type: ignore
    ...

class IMServiceStub:
    """即时通讯接口"""

    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    CreateUser: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.CreateUserRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """新建用户"""
    UpdateUser: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.UpdateUserRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """更新用户"""
    CreateWorkGroup: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.CreateWorkGroupRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """创建Work群组"""
    UpdateWorkGroup: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.UpdateWorkGroupRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """更新Work群组"""
    DeleteWorkGroup: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.DeleteWorkGroupRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """删除Work群组"""
    InviteUserToGroup: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.InviteUserToGroupRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """邀请用户加入群组"""
    RemoveUserFromGroup: grpc.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.RemoveUserFromGroupRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """从群组中移除用户"""

class IMServiceAsyncStub:
    """即时通讯接口"""

    CreateUser: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.CreateUserRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """新建用户"""
    UpdateUser: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.UpdateUserRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """更新用户"""
    CreateWorkGroup: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.CreateWorkGroupRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """创建Work群组"""
    UpdateWorkGroup: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.UpdateWorkGroupRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """更新Work群组"""
    DeleteWorkGroup: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.DeleteWorkGroupRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """删除Work群组"""
    InviteUserToGroup: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.InviteUserToGroupRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """邀请用户加入群组"""
    RemoveUserFromGroup: grpc.aio.UnaryUnaryMultiCallable[
        paperpilot_common.protobuf.im.im_pb2.RemoveUserFromGroupRequest,
        google.protobuf.empty_pb2.Empty,
    ]
    """从群组中移除用户"""

class IMServiceServicer(metaclass=abc.ABCMeta):
    """即时通讯接口"""

    @abc.abstractmethod
    def CreateUser(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.CreateUserRequest,
        context: _ServicerContext,
    ) -> typing.Union[google.protobuf.empty_pb2.Empty, collections.abc.Awaitable[google.protobuf.empty_pb2.Empty]]:
        """新建用户"""
    @abc.abstractmethod
    def UpdateUser(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.UpdateUserRequest,
        context: _ServicerContext,
    ) -> typing.Union[google.protobuf.empty_pb2.Empty, collections.abc.Awaitable[google.protobuf.empty_pb2.Empty]]:
        """更新用户"""
    @abc.abstractmethod
    def CreateWorkGroup(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.CreateWorkGroupRequest,
        context: _ServicerContext,
    ) -> typing.Union[google.protobuf.empty_pb2.Empty, collections.abc.Awaitable[google.protobuf.empty_pb2.Empty]]:
        """创建Work群组"""
    @abc.abstractmethod
    def UpdateWorkGroup(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.UpdateWorkGroupRequest,
        context: _ServicerContext,
    ) -> typing.Union[google.protobuf.empty_pb2.Empty, collections.abc.Awaitable[google.protobuf.empty_pb2.Empty]]:
        """更新Work群组"""
    @abc.abstractmethod
    def DeleteWorkGroup(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.DeleteWorkGroupRequest,
        context: _ServicerContext,
    ) -> typing.Union[google.protobuf.empty_pb2.Empty, collections.abc.Awaitable[google.protobuf.empty_pb2.Empty]]:
        """删除Work群组"""
    @abc.abstractmethod
    def InviteUserToGroup(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.InviteUserToGroupRequest,
        context: _ServicerContext,
    ) -> typing.Union[google.protobuf.empty_pb2.Empty, collections.abc.Awaitable[google.protobuf.empty_pb2.Empty]]:
        """邀请用户加入群组"""
    @abc.abstractmethod
    def RemoveUserFromGroup(
        self,
        request: paperpilot_common.protobuf.im.im_pb2.RemoveUserFromGroupRequest,
        context: _ServicerContext,
    ) -> typing.Union[google.protobuf.empty_pb2.Empty, collections.abc.Awaitable[google.protobuf.empty_pb2.Empty]]:
        """从群组中移除用户"""

def add_IMServiceServicer_to_server(
    servicer: IMServiceServicer, server: typing.Union[grpc.Server, grpc.aio.Server]
) -> None: ...

class IMPublicServiceStub:
    """即时通讯公开接口"""

    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    IMAuth: grpc.UnaryUnaryMultiCallable[
        google.protobuf.empty_pb2.Empty,
        paperpilot_common.protobuf.im.im_pb2.IMAuthResponse,
    ]
    """IM认证"""

class IMPublicServiceAsyncStub:
    """即时通讯公开接口"""

    IMAuth: grpc.aio.UnaryUnaryMultiCallable[
        google.protobuf.empty_pb2.Empty,
        paperpilot_common.protobuf.im.im_pb2.IMAuthResponse,
    ]
    """IM认证"""

class IMPublicServiceServicer(metaclass=abc.ABCMeta):
    """即时通讯公开接口"""

    @abc.abstractmethod
    def IMAuth(
        self,
        request: google.protobuf.empty_pb2.Empty,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.im.im_pb2.IMAuthResponse,
        collections.abc.Awaitable[paperpilot_common.protobuf.im.im_pb2.IMAuthResponse],
    ]:
        """IM认证"""

def add_IMPublicServiceServicer_to_server(
    servicer: IMPublicServiceServicer, server: typing.Union[grpc.Server, grpc.aio.Server]
) -> None: ...
