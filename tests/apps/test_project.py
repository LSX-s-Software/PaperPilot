from uuid import UUID

import pytest
from paperpilot_common.exceptions import ApiException
from paperpilot_common.protobuf.project.project_pb2 import (
    CheckUserJoinedProjectRequest,
    CreateProjectRequest,
    ListProjectRequest,
    ProjectId,
    ProjectInfo,
    ProjectInviteCode,
)
from paperpilot_common.response import ResponseType
from project.models import Project, UserProject
from project.urls import ProjectController, ProjectPublicController


class TestProjectPublic:
    @pytest.fixture
    def api(self):
        return ProjectPublicController()

    @pytest.mark.asyncio
    async def test_list_user_joined_projects(
        self, api, context, projects, user_id
    ):
        context.authenticate(user_id)

        response = await api.ListUserJoinedProjects(
            ListProjectRequest(
                page=1,
                page_size=5,
                order_by="-create_time",
            ),
            context,
        )

        assert response.total == 10
        assert len(response.projects) == 5
        assert response.next_page == 2

        # for i, project in enumerate(response.projects):
        #     assert project.id == projects[i].id.hex
        #     assert project.name == projects[i].name
        #     assert project.description == projects[i].description
        #     assert project.invite_code == projects[i].invite_code

    @pytest.mark.asyncio
    async def test_list_user_joined_projects__empty(
        self, api, context, projects, wrong_user_id
    ):
        context.authenticate(wrong_user_id)

        response = await api.ListUserJoinedProjects(
            ListProjectRequest(
                page=1,
                page_size=10,
                order_by="-create_time",
            ),
            context,
        )

        assert response.total == 0
        assert len(response.projects) == 0

    @pytest.mark.asyncio
    async def test_list_user_joined_projects__no_next_page(
        self, api, context, projects, user_id
    ):
        context.authenticate(user_id)

        response = await api.ListUserJoinedProjects(
            ListProjectRequest(
                page=2,
                page_size=10,
                order_by="-create_time",
            ),
            context,
        )

        assert response.total == 10
        assert len(response.projects) == 0
        assert response.next_page == 0

    @pytest.mark.asyncio
    async def test_list_user_joined_projects__has_next_page(
        self, api, context, projects, user_id
    ):
        context.authenticate(user_id)

        response = await api.ListUserJoinedProjects(
            ListProjectRequest(
                page=1,
                page_size=5,
                order_by="-create_time",
            ),
            context,
        )

        assert response.total == 10
        assert len(response.projects) == 5
        assert response.next_page == 2

    @pytest.mark.asyncio
    async def test_list_user_joined_projects__order_by_name(
        self, api, context, projects, user_id
    ):
        context.authenticate(user_id)

        response = await api.ListUserJoinedProjects(
            ListProjectRequest(
                page=1,
                page_size=5,
                order_by="name",
            ),
            context,
        )

        assert response.total == 10
        assert len(response.projects) == 5
        assert response.next_page == 2

        assert response.projects[0].name < response.projects[1].name

    @pytest.mark.asyncio
    async def test_list_user_joined_projects__order_by_name_desc(
        self, api, context, projects, user_id
    ):
        context.authenticate(user_id)

        response = await api.ListUserJoinedProjects(
            ListProjectRequest(
                page=1,
                page_size=5,
                order_by="-name",
            ),
            context,
        )

        assert response.total == 10
        assert len(response.projects) == 5
        assert response.next_page == 2

        assert response.projects[0].name > response.projects[1].name

    @pytest.mark.asyncio
    async def test_get_project_info(self, api, context, projects, user_id):
        context.authenticate(user_id)

        response = await api.GetProjectInfo(
            ProjectId(
                id=projects[0].id.hex,
            ),
            context,
        )

        assert response.id == projects[0].id.hex
        assert response.name == projects[0].name
        assert response.description == projects[0].description
        assert response.invite_code == projects[0].invite_code
        assert response.owner_id == user_id.hex
        assert len(response.members) == 2

    @pytest.mark.asyncio
    async def test_get_project_info__not_joined(
        self, api, context, projects, wrong_user_id
    ):
        context.authenticate(wrong_user_id)

        with pytest.raises(ApiException) as exc:
            await api.GetProjectInfo(
                ProjectId(
                    id=projects[0].id.hex,
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_get_project_info__not_exist(self, api, context, user_id):
        context.authenticate(user_id)

        with pytest.raises(ApiException) as exc:
            await api.GetProjectInfo(
                ProjectId(
                    id=UUID(int=0).hex,
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_create_project(self, api, context, user_id):
        context.authenticate(user_id)

        response = await api.CreateProject(
            CreateProjectRequest(
                name="test",
                description="test",
            ),
            context,
        )

        assert response.name == "test"
        assert response.description == "test"
        assert response.owner_id == user_id.hex
        assert len(response.members) == 1

    @pytest.mark.asyncio
    async def test_create_project__empty_name(self, api, context, user_id):
        context.authenticate(user_id)

        with pytest.raises(ApiException) as exc:
            await api.CreateProject(
                CreateProjectRequest(
                    name="",
                    description="test",
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.ParamEmpty

    @pytest.mark.asyncio
    async def test_update_project_info(self, api, context, projects, user_id):
        context.authenticate(user_id)

        response = await api.UpdateProjectInfo(
            ProjectInfo(
                id=projects[0].id.hex,
                name="test",
                description="test",
            ),
            context,
        )

        assert response.name == "test"
        assert response.description == "test"
        assert response.owner_id == user_id.hex
        assert len(response.members) == 2

    @pytest.mark.asyncio
    async def test_update_project_info__empty_name(
        self, api, context, projects, user_id
    ):
        context.authenticate(user_id)

        with pytest.raises(ApiException) as exc:
            await api.UpdateProjectInfo(
                ProjectInfo(
                    id=projects[0].id.hex,
                    name="",
                    description="test",
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.ParamEmpty

    @pytest.mark.asyncio
    async def test_update_project_info__member(
        self, api, context, projects, user_id, not_owner_id
    ):
        context.authenticate(not_owner_id)

        response = await api.UpdateProjectInfo(
            ProjectInfo(
                id=projects[0].id.hex,
                name="test",
                description="test",
            ),
            context,
        )

        assert response.name == "test"
        assert response.description == "test"
        assert response.owner_id == user_id.hex
        assert len(response.members) == 2

    @pytest.mark.asyncio
    async def test_update_project_info__not_joined(
        self, api, context, projects, wrong_user_id
    ):
        context.authenticate(wrong_user_id)

        with pytest.raises(ApiException) as exc:
            await api.UpdateProjectInfo(
                ProjectInfo(
                    id=projects[0].id.hex,
                    name="test",
                    description="test",
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_update_project_info__not_exist(self, api, context, user_id):
        context.authenticate(user_id)

        with pytest.raises(ApiException) as exc:
            await api.UpdateProjectInfo(
                ProjectInfo(
                    id=UUID(int=0).hex,
                    name="test",
                    description="test",
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_delete_project(self, api, context, projects, user_id):
        context.authenticate(user_id)

        await api.DeleteProject(
            ProjectId(
                id=projects[0].id.hex,
            ),
            context,
        )

        assert (
            await Project.objects.filter(id=projects[0].id).aexists() is False
        )

    @pytest.mark.asyncio
    async def test_delete_project__member(
        self, api, context, projects, user_id, not_owner_id
    ):
        context.authenticate(not_owner_id)

        with pytest.raises(ApiException) as exc:
            await api.DeleteProject(
                ProjectId(
                    id=projects[0].id.hex,
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_delete_project__not_joined(
        self, api, context, projects, wrong_user_id
    ):
        context.authenticate(wrong_user_id)

        with pytest.raises(ApiException) as exc:
            await api.DeleteProject(
                ProjectId(
                    id=projects[0].id.hex,
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_delete_project__not_exist(self, api, context, user_id):
        context.authenticate(user_id)

        with pytest.raises(ApiException) as exc:
            await api.DeleteProject(
                ProjectId(
                    id=UUID(int=0).hex,
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_join_project(
        self, api, context, projects, user_id, wrong_user_id
    ):
        context.authenticate(wrong_user_id)

        await api.JoinProject(
            ProjectInviteCode(
                invite_code=projects[0].invite_code,
            ),
            context,
        )

        assert await UserProject.objects.filter(
            user_id=wrong_user_id, project_id=projects[0].id
        ).aexists()

    @pytest.mark.asyncio
    async def test_join_project__not_exist(
        self, api, context, projects, user_id, wrong_user_id
    ):
        context.authenticate(wrong_user_id)

        with pytest.raises(ApiException) as exc:
            await api.JoinProject(
                ProjectInviteCode(
                    invite_code="",
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.ResourceNotFound

    @pytest.mark.asyncio
    async def test_join_project__already_joined(
        self, api, context, projects, user_id
    ):
        context.authenticate(user_id)

        await api.JoinProject(
            ProjectInviteCode(
                invite_code=projects[0].invite_code,
            ),
            context,
        )

        assert await UserProject.objects.filter(
            user_id=user_id, project_id=projects[0].id
        ).aexists()

    @pytest.mark.asyncio
    async def test_quit_project(
        self, api, context, projects, user_id, not_owner_id
    ):
        context.authenticate(not_owner_id)

        await api.QuitProject(
            ProjectId(
                id=projects[0].id.hex,
            ),
            context,
        )

        assert (
            await UserProject.objects.filter(
                user_id=not_owner_id, project_id=projects[0].id
            ).aexists()
            is False
        )

    @pytest.mark.asyncio
    async def test_quit_project__owner(self, api, context, projects, user_id):
        context.authenticate(user_id)

        with pytest.raises(ApiException) as exc:
            await api.QuitProject(
                ProjectId(
                    id=projects[0].id.hex,
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_quit_project__not_joined(
        self, api, context, projects, wrong_user_id
    ):
        context.authenticate(wrong_user_id)

        with pytest.raises(ApiException) as exc:
            await api.QuitProject(
                ProjectId(
                    id=projects[0].id.hex,
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.PermissionDenied

    @pytest.mark.asyncio
    async def test_quit_project__not_exist(self, api, context, user_id):
        context.authenticate(user_id)

        with pytest.raises(ApiException) as exc:
            await api.QuitProject(
                ProjectId(
                    id=UUID(int=0).hex,
                ),
                context,
            )

        assert exc.value.response_type == ResponseType.PermissionDenied


class TestProject:
    @pytest.fixture
    def api(self):
        return ProjectController()

    @pytest.mark.asyncio
    async def test_check_user_joined_project__owner(
        self, api, context, projects, user_id
    ):
        response = await api.CheckUserJoinedProject(
            CheckUserJoinedProjectRequest(
                user_id=user_id.hex,
                project_id=projects[0].id.hex,
            ),
            context,
        )

        assert response.value is True

    @pytest.mark.asyncio
    async def test_check_user_joined_project__member(
        self, api, context, projects, user_id, not_owner_id
    ):
        response = await api.CheckUserJoinedProject(
            CheckUserJoinedProjectRequest(
                user_id=not_owner_id.hex,
                project_id=projects[0].id.hex,
            ),
            context,
        )

        assert response.value is True

    @pytest.mark.asyncio
    async def test_check_user_joined_project__not_joined(
        self, api, context, projects, wrong_user_id
    ):
        response = await api.CheckUserJoinedProject(
            CheckUserJoinedProjectRequest(
                user_id=wrong_user_id.hex,
                project_id=projects[0].id.hex,
            ),
            context,
        )

        assert response.value is False
