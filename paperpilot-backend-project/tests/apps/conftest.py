import random
import string
from typing import Tuple
from uuid import UUID

import pytest
import pytest_asyncio
from paperpilot_common.protobuf.user.user_pb2 import (
    UserId,
    UserIdList,
    UserInfo,
    UserInfoMap,
)


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
def user_id(user_mock):
    return UUID("678574dd4a274d3cbfac10666b7613ef")


@pytest.fixture
def owner2_id(user_mock):
    return UUID("678574dd4a274d3cbfac10666b7613e1")


@pytest.fixture
def not_owner_id(user_mock):
    return UUID("678574dd4a274d3cbfac10666b7613e0")


@pytest.fixture
def user_mock(mocker):
    user_info = UserInfo(
        id=UUID("678574dd4a274d3cbfac10666b7613ef").hex,
        username="test-user",
        avatar="/test.jpg",
    )

    owner2_info = UserInfo(
        id=UUID("678574dd4a274d3cbfac10666b7613e1").hex,
        username="test-owner2",
        avatar="/test.jpg",
    )

    not_owner_info = UserInfo(
        id=UUID("678574dd4a274d3cbfac10666b7613e0").hex,
        username="test-not-owner",
        avatar="/test.jpg",
    )

    async def get_info(request: UserId) -> UserInfo:
        if request.id == user_info.id:
            return user_info
        elif request.id == owner2_info.id:
            return owner2_info
        elif request.id == not_owner_info.id:
            return not_owner_info
        else:
            return UserInfo(
                id=request.id, username="unknown", avatar="/test.jpg"
            )

    async def get_infos(request: UserIdList) -> UserInfoMap:
        infos = {}
        for id in request.ids:
            if id == user_info.id:
                infos[id] = user_info
            elif id == owner2_info.id:
                infos[id] = owner2_info
            elif id == not_owner_info.id:
                infos[id] = not_owner_info

        return UserInfoMap(infos=infos)

    get_user_info_mock = mocker.AsyncMock(side_effect=get_info)
    get_user_infos_mock = mocker.AsyncMock(side_effect=get_infos)
    mocker.patch(
        "project.services.ProjectService.user_service.stub.GetUserInfo",
        new=get_user_info_mock,
    )
    mocker.patch(
        "project.services.ProjectService.user_service.stub.GetUserInfos",
        new=get_user_infos_mock,
    )


@pytest.fixture
def wrong_user_id():
    return UUID("678574dd4a274d3cbfac10666b7613ee")


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clear_db(db):
    yield
    from project.models import Project, UserProject

    await Project.objects.all().adelete()
    assert await Project.objects.all().acount() == 0

    await UserProject.objects.all().adelete()
    assert await UserProject.objects.all().acount() == 0


@pytest.fixture
def project_id():
    return UUID("678574dd4a274d3cbfac10666b761300")


@pytest.fixture
def invite_code(mocker):
    code = "NC0coBae4OJGKwT1InbwqBr0hvWlD1JH"

    mocker.patch("project.utils.get_random_invite_code", return_value=code)

    return code


@pytest_asyncio.fixture
async def project(db, project_id, invite_code, user_id, not_owner_id):
    from project.models import Project

    project = await Project.objects.acreate(
        id=project_id,
        name="test",
        description="test",
        invite_code=invite_code,
    )

    await project.users.acreate(
        user_id=user_id,
        is_owner=True,
    )

    await project.users.acreate(
        user_id=not_owner_id,
        is_owner=False,
    )

    return project


@pytest_asyncio.fixture
async def projects(
    db, user_id, not_owner_id, invite_code, project_id, owner2_id
):
    from project.models import Project

    projects = [
        Project(
            name=f"test{i}",
            description="test",
            invite_code="".join(
                random.choices(string.ascii_letters + string.digits, k=32)
            ),
        )
        for i in range(10)
    ]

    projects[0].id = project_id
    projects[0].invite_code = invite_code

    await Project.objects.abulk_create(projects)

    for i, project in enumerate(projects):
        if i < 5:
            await project.users.acreate(
                user_id=user_id,
                is_owner=True,
            )

            await project.users.acreate(
                user_id=not_owner_id,
                is_owner=False,
            )
        else:
            await project.users.acreate(
                user_id=owner2_id,
                is_owner=True,
            )

            await project.users.acreate(
                user_id=user_id,
                is_owner=False,
            )

    return projects


@pytest.fixture(autouse=True, scope="function")
def mock_im_client(mocker):
    mock = mocker.AsyncMock()

    mocker.patch("server.business.grpc.im.IMClient.stub", new=mock)
