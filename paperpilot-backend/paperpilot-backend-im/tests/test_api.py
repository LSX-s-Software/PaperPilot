import pytest


class TestMockIMApi:
    @pytest.fixture
    def api(self, mock_im_api):
        from server.business.im import IMApi

        return IMApi()

    @pytest.mark.asyncio
    async def test_create_user(self, api, user1):
        response = await api.create_user(
            user_id=user1.hex,
            username="test-name",
            avatar="avatar",
        )

        assert response["ErrorCode"] == 0
