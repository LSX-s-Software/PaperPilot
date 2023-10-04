from test.urls import TestPublicController

import pytest
from google.protobuf.empty_pb2 import Empty


class TestTest:
    @pytest.fixture
    def api(self):
        return TestPublicController()

    @pytest.mark.asyncio
    async def test_test__anonymous(
        self,
        api,
        context,
    ):
        response = await api.Test(Empty(), context)

        assert response.time
        assert str(response.user) == ""

    @pytest.mark.asyncio
    async def test_test__user(self, api, context, user_stub, user_id):
        context.authenticate(user_id)
        response = await api.Test(Empty(), context)

        assert response.time
        assert response.user.id == user_id.hex
