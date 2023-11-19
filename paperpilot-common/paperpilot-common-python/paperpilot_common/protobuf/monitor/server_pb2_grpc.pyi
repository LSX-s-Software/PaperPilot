"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import abc
import collections.abc
import google.protobuf.empty_pb2
import grpc
import grpc.aio
import paperpilot_common.protobuf.monitor.server_pb2
import typing

_T = typing.TypeVar("_T")

class _MaybeAsyncIterator(collections.abc.AsyncIterator[_T], collections.abc.Iterator[_T], metaclass=abc.ABCMeta): ...

class _ServicerContext(grpc.ServicerContext, grpc.aio.ServicerContext):  # type: ignore
    ...

class MonitorPublicServiceStub:
    """监控公开服务"""

    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    GetStatus: grpc.UnaryUnaryMultiCallable[
        google.protobuf.empty_pb2.Empty,
        paperpilot_common.protobuf.monitor.server_pb2.ServerStatus,
    ]
    """获取后端状态"""

class MonitorPublicServiceAsyncStub:
    """监控公开服务"""

    GetStatus: grpc.aio.UnaryUnaryMultiCallable[
        google.protobuf.empty_pb2.Empty,
        paperpilot_common.protobuf.monitor.server_pb2.ServerStatus,
    ]
    """获取后端状态"""

class MonitorPublicServiceServicer(metaclass=abc.ABCMeta):
    """监控公开服务"""

    @abc.abstractmethod
    def GetStatus(
        self,
        request: google.protobuf.empty_pb2.Empty,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.monitor.server_pb2.ServerStatus,
        collections.abc.Awaitable[paperpilot_common.protobuf.monitor.server_pb2.ServerStatus],
    ]:
        """获取后端状态"""

def add_MonitorPublicServiceServicer_to_server(
    servicer: MonitorPublicServiceServicer, server: typing.Union[grpc.Server, grpc.aio.Server]
) -> None: ...