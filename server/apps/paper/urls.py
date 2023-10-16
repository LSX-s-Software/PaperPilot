import collections.abc
import typing

import google.protobuf
import google.protobuf.empty_pb2
import google.protobuf.wrappers_pb2
import paperpilot_common.protobuf
import paperpilot_common.protobuf.paper.paper_pb2
from paperpilot_common.middleware.server.auth import AuthMixin
from paperpilot_common.protobuf.paper import paper_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext


def grpc_hook(server):
    paper_pb2_grpc.add_PaperServiceServicer_to_server(PaperController(), server)
    paper_pb2_grpc.add_PaperPublicServiceServicer_to_server(
        PaperPublicController(), server
    )

    return [
        _.full_name
        for _ in dict(
            paperpilot_common.protobuf.paper.paper_pb2.DESCRIPTOR.services_by_name
        ).values()
    ]


class PaperPublicController(
    paper_pb2_grpc.PaperPublicServiceServicer, AuthMixin
):
    async def ListPaper(
        self,
        request: paperpilot_common.protobuf.paper.paper_pb2.ListPaperRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.paper.paper_pb2.ListPaperResponse,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.paper.paper_pb2.ListPaperResponse
        ],
    ]:
        pass

    async def GetPaper(
        self,
        request: paperpilot_common.protobuf.paper.paper_pb2.PaperId,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.paper.paper_pb2.PaperDetail,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.paper.paper_pb2.PaperDetail
        ],
    ]:
        pass

    async def CreatePaper(
        self,
        request: paperpilot_common.protobuf.paper.paper_pb2.CreatePaperRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.paper.paper_pb2.PaperDetail,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.paper.paper_pb2.PaperDetail
        ],
    ]:
        pass

    async def CreatePaperByLink(
        self,
        request: paperpilot_common.protobuf.paper.paper_pb2.CreatePaperByLinkRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.paper.paper_pb2.PaperDetail,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.paper.paper_pb2.PaperDetail
        ],
    ]:
        pass

    async def UpdatePaper(
        self,
        request: paperpilot_common.protobuf.paper.paper_pb2.PaperDetail,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.paper.paper_pb2.PaperDetail,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.paper.paper_pb2.PaperDetail
        ],
    ]:
        pass

    async def UploadAttachment(
        self,
        request: paperpilot_common.protobuf.paper.paper_pb2.UploadAttachmentRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.paper.paper_pb2.UploadAttachmentResponse,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.paper.paper_pb2.UploadAttachmentResponse
        ],
    ]:
        pass

    async def DeletePaper(
        self,
        request: paperpilot_common.protobuf.paper.paper_pb2.PaperId,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        pass


class PaperController(paper_pb2_grpc.PaperServiceServicer):
    async def AddPaper(
        self,
        request: paperpilot_common.protobuf.paper.paper_pb2.CreatePaperRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.paper.paper_pb2.PaperDetail,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.paper.paper_pb2.PaperDetail
        ],
    ]:
        pass

    async def UpdatePaper(
        self,
        request: paperpilot_common.protobuf.paper.paper_pb2.PaperDetail,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.paper.paper_pb2.PaperDetail,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.paper.paper_pb2.PaperDetail
        ],
    ]:
        pass
