import collections.abc
import typing
from test.services import test_service

import google.protobuf
import google.protobuf.empty_pb2
import paperpilot_common.protobuf
import paperpilot_common.protobuf.test.test_pb2
from paperpilot_common.middleware.server.auth import AuthMixin
from paperpilot_common.protobuf.test import test_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext


def grpc_hook(server):
    test_pb2_grpc.add_TestPublicServiceServicer_to_server(
        TestPublicController(), server
    )

    return [
        _.full_name
        for _ in dict(
            paperpilot_common.protobuf.test.test_pb2.DESCRIPTOR.services_by_name
        ).values()
    ]


class TestPublicController(test_pb2_grpc.TestPublicServiceServicer, AuthMixin):
    logger = test_service.logger

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
        self.logger.info(dict(context.invocation_metadata()))
        if self.user.is_anonymous:
            return await test_service.get_anonymous_test()
        else:
            return await test_service.get_user_test(self.user.id)
