from uuid import UUID

import pytest
from paperpilot_common.grpc.context import FakeServicerContext
from paperpilot_common.protobuf.user.user_pb2 import UserInfo
from paperpilot_common.protobuf.user.user_pb2_grpc import UserServiceStub


@pytest.fixture
def context():
    return FakeServicerContext()


@pytest.fixture
def user_id():
    return UUID("678574dd4a274d3cbfac10666b7613ef")


@pytest.fixture
def user_info(user_id):
    return UserInfo(
        id=user_id.hex,
        username="test",
        avatar="test.jpg",
    )


@pytest.fixture
def user_stub(mocker, user_info) -> UserServiceStub:
    stub = mocker.Mock()

    stub.GetUserInfo = mocker.AsyncMock(return_value=user_info)

    from server.business.grpc.user import user_client

    user_client._stub = stub

    return user_client.stub
