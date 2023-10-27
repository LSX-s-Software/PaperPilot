import google.protobuf.empty_pb2
import pytest
from paperpilot_common.protobuf.im.im_pb2 import (
    CreateUserRequest,
    CreateWorkGroupRequest,
    DeleteWorkGroupRequest,
    InviteUserToGroupRequest,
    RemoveUserFromGroupRequest,
    UpdateUserRequest,
    UpdateWorkGroupRequest,
)


class TestIm:
    def is_empty(self, obj):
        return isinstance(obj, google.protobuf.empty_pb2.Empty)

    @pytest.fixture
    def api(self, mock_im_api):
        from server.apps.im.urls import IMController

        return IMController()

    @pytest.mark.asyncio
    async def test_create_user(self, api, context, user1):
        response = await api.CreateUser(
            CreateUserRequest(
                id=user1.hex,
                username="test-name",
                avatar="avatar",
            ),
            context,
        )

        assert self.is_empty(response)

    @pytest.mark.asyncio
    async def test_update_user(self, api, context, user1):
        response = await api.UpdateUser(
            UpdateUserRequest(
                id=user1.hex,
                username="test-name",
                avatar="avatar",
            ),
            context,
        )

        assert self.is_empty(response)

    @pytest.mark.asyncio
    async def test_create_work_group(self, api, context, user1, group):
        response = await api.CreateWorkGroup(
            CreateWorkGroupRequest(
                owner=user1.hex,
                name="test-name",
                id=group.hex,
            ),
            context,
        )

        assert self.is_empty(response)

    @pytest.mark.asyncio
    async def test_update_work_group(self, api, context, group):
        response = await api.UpdateWorkGroup(
            UpdateWorkGroupRequest(
                id=group.hex,
                name="test-name2",
            ),
            context,
        )

        assert self.is_empty(response)

    @pytest.mark.asyncio
    async def test_create_group_member(self, api, context, user1, group):
        response = await api.InviteUserToGroup(
            InviteUserToGroupRequest(
                group_id=group.hex,
                user_id=user1.hex,
            ),
            context,
        )

        assert self.is_empty(response)

    @pytest.mark.asyncio
    async def test_delete_group_member(self, api, context, user1, group):
        response = await api.RemoveUserFromGroup(
            RemoveUserFromGroupRequest(
                group_id=group.hex,
                user_id=user1.hex,
            ),
            context,
        )

        assert self.is_empty(response)

    @pytest.mark.asyncio
    async def test_delete_work_group(self, api, context, group):
        response = await api.DeleteWorkGroup(
            DeleteWorkGroupRequest(
                id=group.hex,
            ),
            context,
        )

        assert self.is_empty(response)


class TestIMPublic:
    @pytest.fixture
    def api(self, mock_im_api):
        from server.apps.im.urls import IMPublicController

        return IMPublicController()

    @pytest.mark.asyncio
    async def test_auth(self, api, context, user1):
        context.authenticate(user1)

        response = await api.IMAuth(google.protobuf.empty_pb2.Empty(), context)

        assert response.id == user1.hex
        assert response.sig != ""
