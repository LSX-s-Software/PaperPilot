import collections.abc
import typing

import google.protobuf.empty_pb2
import paperpilot_common.protobuf
from paperpilot_common.protobuf.monitor import server_pb2, server_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext
from starlette.routing import Route

from .services import monitor_service
from .views import StatusSvgView

routes = [
    Route("/", StatusSvgView),
]


def grpc_hook(server):
    server_pb2_grpc.add_MonitorPublicServiceServicer_to_server(
        MonitorPublicController(), server
    )

    return [
        _.full_name
        for _ in dict(server_pb2.DESCRIPTOR.services_by_name).values()
    ]


class MonitorPublicController(server_pb2_grpc.MonitorPublicServiceServicer):
    async def GetStatus(
        self,
        request: google.protobuf.empty_pb2.Empty,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.monitor.server_pb2.ServerStatus,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.monitor.server_pb2.ServerStatus
        ],
    ]:
        return await monitor_service.get_status()
