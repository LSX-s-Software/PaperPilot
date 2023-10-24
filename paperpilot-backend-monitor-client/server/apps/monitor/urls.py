import collections.abc
import typing

import google.protobuf.empty_pb2
import paperpilot_common.protobuf
from paperpilot_common.protobuf.monitor import client_pb2, client_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext

from .services import monitor_service


def grpc_hook(server):
    client_pb2_grpc.add_MonitorClientServiceServicer_to_server(
        MonitorClientController(), server
    )

    return [
        _.full_name
        for _ in dict(client_pb2.DESCRIPTOR.services_by_name).values()
    ]


class MonitorClientController(client_pb2_grpc.MonitorClientServiceServicer):
    async def GetStatus(
        self,
        request: google.protobuf.empty_pb2.Empty,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.monitor.client_pb2.ClientStatus,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.monitor.client_pb2.ClientStatus
        ],
    ]:
        return await monitor_service.get_status()
