"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import abc
import collections.abc
import google.protobuf.empty_pb2
import grpc
import grpc.aio
import paperpilot_common.protobuf.test.test_pb2
import typing

_T = typing.TypeVar("_T")

class _MaybeAsyncIterator(collections.abc.AsyncIterator[_T], collections.abc.Iterator[_T], metaclass=abc.ABCMeta): ...

class _ServicerContext(grpc.ServicerContext, grpc.aio.ServicerContext):  # type: ignore
    ...

class TestPublicServiceStub:
    """测试公开接口"""

    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    Test: grpc.UnaryUnaryMultiCallable[
        google.protobuf.empty_pb2.Empty,
        paperpilot_common.protobuf.test.test_pb2.TestResult,
    ]
    """测试接口"""

class TestPublicServiceAsyncStub:
    """测试公开接口"""

    Test: grpc.aio.UnaryUnaryMultiCallable[
        google.protobuf.empty_pb2.Empty,
        paperpilot_common.protobuf.test.test_pb2.TestResult,
    ]
    """测试接口"""

class TestPublicServiceServicer(metaclass=abc.ABCMeta):
    """测试公开接口"""

    @abc.abstractmethod
    def Test(
        self,
        request: google.protobuf.empty_pb2.Empty,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.test.test_pb2.TestResult,
        collections.abc.Awaitable[paperpilot_common.protobuf.test.test_pb2.TestResult],
    ]:
        """测试接口"""

def add_TestPublicServiceServicer_to_server(
    servicer: TestPublicServiceServicer, server: typing.Union[grpc.Server, grpc.aio.Server]
) -> None: ...