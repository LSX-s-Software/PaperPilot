from typing import Tuple
from uuid import UUID

import pytest
import pytest_asyncio
from django.utils import timezone


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
def user_id():
    return UUID("678574dd4a274d3cbfac10666b7613ef")


@pytest.fixture
def username():
    return "test-username"


@pytest.fixture
def password():
    return "test-password"


@pytest.fixture
def phone():
    return "18312341234"


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clear_db(db):
    yield
    from user.models import User

    await User.objects.all().adelete()
    assert await User.objects.all().acount() == 0


@pytest_asyncio.fixture
async def user(db, user_id, username, phone, password):
    from django.contrib.auth.hashers import make_password
    from user.models import User

    await User.objects.filter(id=user_id).adelete()

    user = User(
        id=user_id,
        username=username,
        phone=phone,
        password=make_password(password),
        last_login=timezone.now(),
    )

    await user.asave()

    return user


@pytest.fixture
def code(mocker, phone):
    _code = "123456"

    import oauth.utils as utils

    utils.random_code = mocker.Mock(return_value=_code)

    return _code


@pytest.fixture(autouse=True, scope="function")
def mock_im_client(mocker):
    mock = mocker.AsyncMock()

    mocker.patch("server.business.grpc.im.IMClient.stub", new=mock)
