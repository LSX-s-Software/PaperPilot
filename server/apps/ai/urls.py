import collections.abc
import typing

import paperpilot_common.protobuf
from paperpilot_common.protobuf.ai import ai_pb2, ai_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext

from .services import ai_service


def grpc_hook(server):
    ai_pb2_grpc.add_GptServiceServicer_to_server(AiController(), server)

    return [
        _.full_name for _ in dict(ai_pb2.DESCRIPTOR.services_by_name).values()
    ]


class AiController(ai_pb2_grpc.GptServiceServicer):
    async def Ask(
        self,
        request: paperpilot_common.protobuf.ai.ai_pb2.GptRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        collections.abc.Iterator[
            paperpilot_common.protobuf.ai.ai_pb2.GptResult
        ],
        collections.abc.AsyncIterator[
            paperpilot_common.protobuf.ai.ai_pb2.GptResult
        ],
    ]:
        async for result in ai_service.ask(request.text, request.action):
            yield result
