import collections.abc
import typing
import uuid

import google.protobuf
import google.protobuf.empty_pb2
import google.protobuf.wrappers_pb2
import paperpilot_common.protobuf
import paperpilot_common.protobuf.paper.paper_pb2
from paperpilot_common.middleware.server.auth import AuthMixin
from paperpilot_common.oss.direct import generate_direct_upload_token
from paperpilot_common.oss.utils import get_random_name
from paperpilot_common.protobuf.paper import paper_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext

from .models import Paper
from .services import paper_service


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
        papers, total, next_page = await paper_service.get_paper_list(
            user_id=self.user.id,
            project_id=uuid.UUID(request.project_id),
            page=request.page or 1,
            page_size=request.page_size or 20,
            order_by=request.order_by or "-create_time",
        )

        return paperpilot_common.protobuf.paper.paper_pb2.ListPaperResponse(
            papers=papers,
            total=total,
            next_page=next_page,
        )

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
        return await paper_service.get_paper(
            paper_id=uuid.UUID(request.id),
            user_id=self.user.id,
        )

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
        paper = await paper_service.create_paper_user(
            user_id=self.user.id,
            project_id=uuid.UUID(request.project_id),
            vo=request.paper,
        )

        return paper

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
        paper = await paper_service.update_paper_user(
            user_id=self.user.id,
            paper_id=uuid.UUID(request.id),
            vo=request,
        )

        return paper

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
        token = generate_direct_upload_token(
            callback_url=f"callback/paper/file/?id={request.paper_id}",
            content_type=["application/pdf"],
            key=f"{Paper.FILE_PATH}/{get_random_name('.pdf')}",
            min_size="1b",
            max_size="10mb",
        )
        return (
            paperpilot_common.protobuf.paper.paper_pb2.UploadAttachmentResponse(
                token=token.to_protobuf()
            )
        )

    async def DeletePaper(
        self,
        request: paperpilot_common.protobuf.paper.paper_pb2.PaperId,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        await paper_service.delete_paper(
            user_id=self.user.id,
            paper_id=uuid.UUID(request.id),
        )

        return google.protobuf.empty_pb2.Empty()


class PaperController(paper_pb2_grpc.PaperServiceServicer):
    async def AddPaper(
        self,
        request: paperpilot_common.protobuf.paper.paper_pb2.PaperDetail,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.paper.paper_pb2.PaperDetail,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.paper.paper_pb2.PaperDetail
        ],
    ]:
        return await paper_service.create_paper(vo=request)

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
        return await paper_service.update_paper(
            paper_id=uuid.UUID(request.id),
            vo=request,
        )
