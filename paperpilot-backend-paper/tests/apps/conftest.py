import uuid
from typing import Tuple
from uuid import UUID

import pytest
import pytest_asyncio
from django.utils import timezone
from google.protobuf.wrappers_pb2 import BoolValue
from model_bakery import baker


class FakeServicerContext:
    """
    Implementation of basic RpcContext methods that stores data
    for validation in tests
    """

    def __init__(self):
        self.abort_status = None
        self.abort_message = ""
        self._invocation_metadata = tuple()
        self._trailing_metadata = dict()

    def abort(self, status, message):
        """
        gRPC method that is called on RPC exit
        """
        self.abort_status = status
        self.abort_message = message
        raise Exception()  # Just like original context

    def set_trailing_metadata(self, items: Tuple[Tuple[str, str]]):
        """
        gRPC method that is called to set response metadata
        """
        self._trailing_metadata = {d[0]: d[1] for d in items}

    def get_trailing_metadata(self, key: str):
        """
        Helper to retrieve response metadata value by key
        """
        return self._trailing_metadata[key]

    def invocation_metadata(self) -> Tuple[Tuple[str, str]]:
        """
        gRPC method that retrieves request metadata
        """
        return self._invocation_metadata

    def set_invocation_metadata(self, items: Tuple[Tuple[str, str]]):
        """
        Helper to emulate request metadata
        """
        self._invocation_metadata = items

    def authenticate(self, user_id: UUID | str):
        """
        add user_id to metadata
        """
        if isinstance(user_id, UUID):
            user_id = user_id.hex

        from paperpilot_common.middleware.server.auth import (
            UserContext,
            user_context,
        )

        user_context.set(UserContext(user_id))


@pytest.fixture
def context():
    return FakeServicerContext()


@pytest.fixture
def user_id(mocker):
    user_id = UUID("678574dd4a274d3cbfac10666b7613ef")

    mock = mocker.AsyncMock(return_value=BoolValue(value=True))

    mocker.patch(
        "paper.services.PaperService.project.stub.CheckUserJoinedProject",
        new=mock,
    )

    return user_id


@pytest.fixture
def wrong_user_id(mocker):
    user_id = UUID("678574dd4a274d3cbfac10666b7613ee")

    mock = mocker.AsyncMock(return_value=BoolValue(value=False))

    mocker.patch(
        "paper.services.PaperService.project.stub.CheckUserJoinedProject",
        new=mock,
    )

    return user_id


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clear_db(db):
    yield
    from paper.models import Paper

    await Paper.objects.all().adelete()
    assert await Paper.objects.all().acount() == 0


@pytest.fixture
def project_id():
    return UUID("678574dd4a274d3cbfac10666b761300")


@pytest_asyncio.fixture
async def papers(db, project_id) -> list[UUID]:
    from paper.models import Paper

    await Paper.objects.filter(project_id=project_id).adelete()

    papers = baker.prepare(
        Paper,
        project_id=project_id,
        keywords=["test-keyword1", "test-keyword2", "test-keyword3"],
        authors=["test-author1", "test-author2", "test-author3"],
        tags=["test-tag1", "test-tag2", "test-tag3"],
        publication_year=2023,
        create_time=timezone.now(),
        update_time=timezone.now(),
        _quantity=10,
    )

    await Paper.objects.abulk_create(papers)

    return [paper.id for paper in papers]


@pytest.fixture
def paper_detail():
    from paperpilot_common.protobuf.paper.paper_pb2 import PaperDetail

    return PaperDetail(
        title="test",
        abstract="test",
        keywords=["test"],
        authors=["test"],
        tags=["test"],
        publication_year=2023,
        publication="test",
        event="test",
        volume="test",
        issue="test",
        pages="test",
        doi="test",
        url="test",
    )
