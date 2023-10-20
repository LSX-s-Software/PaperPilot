import collections.abc
import typing

import paperpilot_common.protobuf
import paperpilot_common.protobuf.translation.translation_pb2
from paperpilot_common.middleware.server.auth import AuthMixin
from paperpilot_common.protobuf.translation import translation_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext

from .services import translation_service


def grpc_hook(server):
    translation_pb2_grpc.add_TranslationPublicServiceServicer_to_server(
        TranslationPublicController(), server
    )

    return [
        _.full_name
        for _ in dict(
            paperpilot_common.protobuf.translation.translation_pb2.DESCRIPTOR.services_by_name
        ).values()
    ]


class TranslationPublicController(
    translation_pb2_grpc.TranslationPublicServiceServicer, AuthMixin
):
    async def translate(
        self,
        request: paperpilot_common.protobuf.translation.translation_pb2.TranslationRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.translation.translation_pb2.TranslationResponse,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.translation.translation_pb2.TranslationResponse
        ],
    ]:
        result = await translation_service.translate(
            content=request.content,
            source_language=request.source_language,
            target_language=request.target_language,
        )

        return paperpilot_common.protobuf.translation.translation_pb2.TranslationResponse(
            result=result
        )
