import uuid

import pytest
import pytz
from django.utils import timezone
from paper.models import Paper
from paper.urls import PaperController, PaperPublicController
from paperpilot_common.exceptions import ApiException
from paperpilot_common.protobuf.paper.paper_pb2 import UpdateAttachmentRequest
from paperpilot_common.response import ResponseType


class TestPaperPublic:
    @pytest.fixture
    def api(self):
        return PaperPublicController()

    @pytest.mark.asyncio
    async def test_list_paper(self, api, context, user_id, project_id, papers):
        from paperpilot_common.protobuf.paper.paper_pb2 import ListPaperRequest

        request = ListPaperRequest(
            project_id=project_id.hex,
        )

        context.authenticate(user_id)

        response = await api.ListPaper(request, context)

        assert len(response.papers) == 10
        assert response.total == 10
        assert response.next_page == 0

    @pytest.mark.asyncio
    async def test_list_paper__wrong_user(
        self, api, context, wrong_user_id, project_id, papers
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import ListPaperRequest

        request = ListPaperRequest(
            project_id=project_id.hex,
        )

        context.authenticate(wrong_user_id)

        with pytest.raises(ApiException) as exc:
            await api.ListPaper(request, context)

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_list_paper__empty(self, api, context, user_id, project_id):
        from paperpilot_common.protobuf.paper.paper_pb2 import ListPaperRequest

        request = ListPaperRequest(
            project_id=project_id.hex,
        )

        context.authenticate(user_id)

        response = await api.ListPaper(request, context)

        assert len(response.papers) == 0
        assert response.total == 0
        assert response.next_page == 0

    @pytest.mark.asyncio
    async def test_list_paper__next_page(
        self, api, context, user_id, project_id, papers
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import ListPaperRequest

        request = ListPaperRequest(
            project_id=project_id.hex,
            page_size=5,
        )

        context.authenticate(user_id)

        response = await api.ListPaper(request, context)

        assert len(response.papers) == 5
        assert response.total == 10
        assert response.next_page == 2

    @pytest.mark.asyncio
    async def test_list_paper__order_by(
        self, api, context, user_id, project_id, papers
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import ListPaperRequest

        request = ListPaperRequest(
            project_id=project_id.hex,
            order_by="title",
        )

        context.authenticate(user_id)

        response = await api.ListPaper(request, context)

        assert len(response.papers) == 10
        assert response.total == 10
        assert response.next_page == 0

        assert response.papers[0].title < response.papers[1].title

    @pytest.mark.asyncio
    async def test_list_paper__order_by_desc(
        self, api, context, user_id, project_id, papers
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import ListPaperRequest

        request = ListPaperRequest(
            project_id=project_id.hex,
            order_by="-title",
        )

        context.authenticate(user_id)

        response = await api.ListPaper(request, context)

        assert len(response.papers) == 10
        assert response.total == 10
        assert response.next_page == 0

        assert response.papers[0].title > response.papers[1].title

    @pytest.mark.asyncio
    async def test_get_paper__success(
        self, api, context, user_id, project_id, papers
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import PaperId

        request = PaperId(
            id=papers[0].hex,
        )

        context.authenticate(user_id)

        response = await api.GetPaper(request, context)

        paper = await Paper.objects.aget(id=papers[0])

        assert response.id == paper.id.hex
        assert response.title == paper.title
        assert response.abstract == paper.abstract
        assert response.keywords == paper.keywords
        assert response.authors == paper.authors
        assert response.tags == paper.tags
        assert response.publication_year == paper.publication_year
        assert response.publication == paper.publication
        assert response.volume == paper.volume
        assert response.issue == paper.issue
        assert response.pages == paper.pages
        assert response.doi == paper.doi
        assert response.url == paper.url
        assert (
            response.create_time.ToDatetime(tzinfo=pytz.utc)
            == paper.create_time
        )
        assert (
            response.update_time.ToDatetime(tzinfo=pytz.utc)
            == paper.update_time
        )
        assert response.event == paper.event

    @pytest.mark.asyncio
    async def test_get_paper__wrong_user(
        self, api, context, wrong_user_id, project_id, papers
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import PaperId

        request = PaperId(
            id=papers[0].hex,
        )

        context.authenticate(wrong_user_id)

        with pytest.raises(ApiException) as exc:
            await api.GetPaper(request, context)

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_get_paper__not_found(
        self, api, context, user_id, project_id, papers
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import PaperId

        request = PaperId(id=uuid.UUID(int=0).hex)

        context.authenticate(user_id)

        with pytest.raises(ApiException) as exc:
            await api.GetPaper(request, context)

        assert exc.value.response_type == ResponseType.ResourceNotFound

    @pytest.mark.asyncio
    async def test_create_paper(
        self, api, context, user_id, project_id, paper_detail
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import (
            CreatePaperRequest,
            PaperDetail,
        )

        request = CreatePaperRequest(
            project_id=project_id.hex,
            paper=paper_detail,
        )

        context.authenticate(user_id)

        response = await api.CreatePaper(request, context)

        assert response.title == request.paper.title
        assert response.abstract == request.paper.abstract
        assert response.keywords == request.paper.keywords
        assert response.authors == request.paper.authors
        assert response.tags == request.paper.tags
        assert response.publication_year == request.paper.publication_year
        assert response.publication == request.paper.publication
        assert response.volume == request.paper.volume
        assert response.issue == request.paper.issue
        assert response.pages == request.paper.pages
        assert response.doi == request.paper.doi
        assert response.url == request.paper.url
        assert (
            response.create_time.ToDatetime(tzinfo=pytz.utc) <= timezone.now()
        )
        assert (
            response.update_time.ToDatetime(tzinfo=pytz.utc) <= timezone.now()
        )
        assert response.event == request.paper.event

        assert response.project_id == project_id.hex

    @pytest.mark.asyncio
    async def test_create_paper__least_info(
        self, api, context, user_id, project_id
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import (
            CreatePaperRequest,
            PaperDetail,
        )

        request = CreatePaperRequest(
            project_id=project_id.hex,
            paper=PaperDetail(
                title="test",
            ),
        )

        context.authenticate(user_id)

        response = await api.CreatePaper(request, context)

        assert response.title == request.paper.title
        assert response.abstract == ""
        assert response.keywords == []
        assert response.authors == []
        assert response.tags == []
        assert response.publication_year == 0
        assert response.publication == ""
        assert response.volume == ""
        assert response.issue == ""
        assert response.pages == ""
        assert response.doi == ""
        assert response.url == ""
        assert (
            response.create_time.ToDatetime(tzinfo=pytz.utc) <= timezone.now()
        )
        assert (
            response.update_time.ToDatetime(tzinfo=pytz.utc) <= timezone.now()
        )
        assert response.event == ""

        assert response.project_id == project_id.hex

    @pytest.mark.asyncio
    async def test_create_paper__wrong_user(
        self, api, context, wrong_user_id, project_id
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import (
            CreatePaperRequest,
            PaperDetail,
        )

        request = CreatePaperRequest(
            project_id=project_id.hex,
            paper=PaperDetail(
                title="test",
            ),
        )

        context.authenticate(wrong_user_id)

        with pytest.raises(ApiException) as exc:
            await api.CreatePaper(request, context)

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_update_paper(
        self, api, context, user_id, project_id, papers, paper_detail
    ):
        paper = await Paper.objects.aget(id=papers[0])

        context.authenticate(user_id)

        paper_detail.id = paper.id.hex
        paper_detail.project_id = uuid.UUID(int=0).hex

        response = await api.UpdatePaper(paper_detail, context)

        assert response.title == paper_detail.title
        assert response.title == paper_detail.title
        assert response.abstract == paper_detail.abstract
        assert response.keywords == paper_detail.keywords
        assert response.authors == paper_detail.authors
        assert response.tags == paper_detail.tags
        assert response.publication_year == paper_detail.publication_year
        assert response.publication == paper_detail.publication
        assert response.volume == paper_detail.volume
        assert response.issue == paper_detail.issue
        assert response.pages == paper_detail.pages
        assert response.doi == paper_detail.doi
        assert response.url == paper_detail.url
        assert (
            response.create_time.ToDatetime(tzinfo=pytz.utc)
            == paper.create_time
        )
        assert (
            response.update_time.ToDatetime(tzinfo=pytz.utc)
            != paper.update_time
        )
        assert response.event == paper_detail.event

        assert response.project_id == project_id.hex

    @pytest.mark.asyncio
    async def test_update_paper__not_found(
        self, api, context, user_id, project_id, paper_detail
    ):
        paper_detail.id = uuid.UUID(int=0).hex

        context.authenticate(user_id)

        with pytest.raises(ApiException) as exc:
            await api.UpdatePaper(paper_detail, context)

        assert exc.value.response_type == ResponseType.ResourceNotFound

    @pytest.mark.asyncio
    async def test_delete_paper(
        self, api, context, user_id, project_id, papers
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import PaperId

        request = PaperId(
            id=papers[0].hex,
        )

        context.authenticate(user_id)

        await api.DeletePaper(request, context)

        assert await Paper.objects.filter(id=papers[0]).acount() == 0

    @pytest.mark.asyncio
    async def test_delete_paper__not_found(
        self, api, context, user_id, project_id
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import PaperId

        request = PaperId(
            id=uuid.UUID(int=0).hex,
        )

        context.authenticate(user_id)

        with pytest.raises(ApiException) as exc:
            await api.DeletePaper(request, context)

        assert exc.value.response_type == ResponseType.ResourceNotFound

    @pytest.mark.asyncio
    async def test_create_paper_by_link(
        self, api, context, user_id, project_id
    ):
        from paperpilot_common.protobuf.paper.paper_pb2 import (
            CreatePaperByLinkRequest,
        )

        request = CreatePaperByLinkRequest(
            project_id=project_id.hex,
            link="https://ieeexplore.ieee.org/abstract/document/8952379",
        )

        context.authenticate(user_id)

        response = await api.CreatePaperByLink(request, context)
        assert response.project_id == project_id.hex
        assert response.file != ""
        assert (
            response.title
            == "RANDR: Record and Replay for Android Applications via Targeted Runtime Instrumentation"
        )


class TestPaperController:
    @pytest.fixture
    def api(self):
        return PaperController()

    @pytest.mark.asyncio
    async def test_add_paper(self, api, context, project_id, paper_detail):
        paper_detail.project_id = project_id.hex
        paper_detail.file = "test.pdf"

        response = await api.AddPaper(paper_detail, context)

        assert response.title == paper_detail.title
        assert response.abstract == paper_detail.abstract
        assert response.keywords == paper_detail.keywords
        assert response.authors == paper_detail.authors
        assert response.tags == paper_detail.tags
        assert response.publication_year == paper_detail.publication_year
        assert response.publication == paper_detail.publication
        assert response.volume == paper_detail.volume
        assert response.issue == paper_detail.issue
        assert response.pages == paper_detail.pages
        assert response.doi == paper_detail.doi
        assert response.url == paper_detail.url
        assert (
            response.create_time.ToDatetime(tzinfo=pytz.utc) <= timezone.now()
        )
        assert (
            response.update_time.ToDatetime(tzinfo=pytz.utc) <= timezone.now()
        )
        assert response.event == paper_detail.event

        assert response.project_id == project_id.hex
        assert response.file == "/test.pdf"

    @pytest.mark.asyncio
    async def test_add_paper__least_info(self, api, context, project_id):
        from paperpilot_common.protobuf.paper.paper_pb2 import PaperDetail

        paper_detail = PaperDetail(
            title="test",
        )
        paper_detail.project_id = project_id.hex

        response = await api.AddPaper(paper_detail, context)

        assert response.title == paper_detail.title
        assert response.abstract == ""
        assert response.keywords == []
        assert response.authors == []
        assert response.tags == []
        assert response.publication_year == 0
        assert response.publication == ""
        assert response.volume == ""
        assert response.issue == ""
        assert response.pages == ""
        assert response.doi == ""
        assert response.url == ""
        assert (
            response.create_time.ToDatetime(tzinfo=pytz.utc) <= timezone.now()
        )
        assert (
            response.update_time.ToDatetime(tzinfo=pytz.utc) <= timezone.now()
        )
        assert response.event == ""

        assert response.project_id == project_id.hex
        assert response.file == ""

    @pytest.mark.asyncio
    async def test_update_paper(
        self, api, context, project_id, paper_detail, papers
    ):
        paper = await Paper.objects.aget(id=papers[0])

        paper_detail.project_id = uuid.UUID(int=0).hex
        paper_detail.id = paper.id.hex
        paper_detail.file = "test.pdf"

        response = await api.UpdatePaper(paper_detail, context)

        assert response.title == paper_detail.title
        assert response.abstract == paper_detail.abstract
        assert response.keywords == paper_detail.keywords
        assert response.authors == paper_detail.authors
        assert response.tags == paper_detail.tags
        assert response.publication_year == paper_detail.publication_year
        assert response.publication == paper_detail.publication
        assert response.volume == paper_detail.volume
        assert response.issue == paper_detail.issue
        assert response.pages == paper_detail.pages
        assert response.doi == paper_detail.doi
        assert response.url == paper_detail.url
        assert (
            response.create_time.ToDatetime(tzinfo=pytz.utc)
            == paper.create_time
        )
        assert (
            response.update_time.ToDatetime(tzinfo=pytz.utc)
            >= paper.update_time
        )
        assert response.event == paper_detail.event

        assert response.project_id == uuid.UUID(int=0).hex
        assert response.file == "/test.pdf"

    @pytest.mark.asyncio
    async def test_update_attachment(
        self, api, context, project_id, paper_detail, papers
    ):
        paper = await Paper.objects.aget(id=papers[0])

        response = await api.UpdateAttachment(
            UpdateAttachmentRequest(
                paper_id=paper.id.hex,
                file="paper/test.pdf",
                fetch_metadata=False,
            ),
            context,
        )

        assert response.id == paper.id.hex
        assert response.file == "/paper/test.pdf"

        assert (
            await Paper.objects.aget(id=paper.id)
        ).file.name == "paper/test.pdf"
