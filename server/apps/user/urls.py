import collections.abc
import typing

import google.protobuf.empty_pb2
import paperpilot_common.protobuf.test.test_pb2
from paperpilot_common.protobuf.test import test_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext

from .services import test_service


def grpc_hook(server):
    test_pb2_grpc.add_TestPublicServiceServicer_to_server(
        TestController(), server
    )


class TestController(test_pb2_grpc.TestPublicServiceServicer):
    async def Test(
        self,
        request: google.protobuf.empty_pb2.Empty,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.test.test_pb2.TestResult,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.test.test_pb2.TestResult
        ],
    ]:
        return await test_service.get_test_result(request, context)
