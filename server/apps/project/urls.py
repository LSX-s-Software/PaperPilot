import collections.abc
import typing
from uuid import UUID

import google.protobuf
import google.protobuf.empty_pb2
import google.protobuf.wrappers_pb2
import paperpilot_common.protobuf
import paperpilot_common.protobuf.project.project_pb2
from paperpilot_common.middleware.server.auth import AuthMixin
from paperpilot_common.protobuf.project import project_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext
from starlette.routing import Route

from .services import project_service
from .views import InvitationView

routes = [
    Route("/invitation/", InvitationView),
]


def grpc_hook(server):
    project_pb2_grpc.add_ProjectServiceServicer_to_server(
        ProjectController(), server
    )
    project_pb2_grpc.add_ProjectPublicServiceServicer_to_server(
        ProjectPublicController(), server
    )

    return [
        _.full_name
        for _ in dict(
            paperpilot_common.protobuf.project.project_pb2.DESCRIPTOR.services_by_name
        ).values()
    ]


class ProjectPublicController(
    project_pb2_grpc.ProjectPublicServiceServicer, AuthMixin
):
    async def ListUserJoinedProjects(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ListProjectRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.project.project_pb2.ListProjectResponse,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.project.project_pb2.ListProjectResponse
        ],
    ]:
        return await project_service.list_user_joined_projects(
            user_id=self.user.id,
            page=request.page or 1,
            page_size=request.page_size or 20,
            order_by=request.order_by or "-create_time",
        )

    async def GetProjectInfo(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ProjectId,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.project.project_pb2.ProjectInfo
        ],
    ]:
        return await project_service.get_project_info(
            user_id=self.user.id,
            project=UUID(request.id),
        )

    async def CreateProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.CreateProjectRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.project.project_pb2.ProjectInfo
        ],
    ]:
        return await project_service.create_project(
            user_id=self.user.id,
            name=request.name,
            description=request.description,
        )

    async def UpdateProjectInfo(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.UpdateProjectRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.project.project_pb2.ProjectInfo
        ],
    ]:
        return await project_service.update_project(
            user_id=self.user.id, request=request
        )

    async def DeleteProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ProjectId,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        await project_service.delete_project(
            user_id=self.user.id, project_id=UUID(request.id)
        )
        return google.protobuf.empty_pb2.Empty()

    async def JoinProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ProjectInviteCode,
        context: _ServicerContext,
    ) -> typing.Union[
        paperpilot_common.protobuf.project.project_pb2.ProjectInfo,
        collections.abc.Awaitable[
            paperpilot_common.protobuf.project.project_pb2.ProjectInfo
        ],
    ]:
        return await project_service.join_project(
            user_id=self.user.id, invite_code=request.invite_code
        )

    async def QuitProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ProjectId,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        await project_service.quit_project(
            user_id=self.user.id, project_id=UUID(request.id)
        )
        return google.protobuf.empty_pb2.Empty()


class ProjectController(project_pb2_grpc.ProjectServiceServicer):
    async def CheckUserJoinedProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.CheckUserJoinedProjectRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.wrappers_pb2.BoolValue,
        collections.abc.Awaitable[google.protobuf.wrappers_pb2.BoolValue],
    ]:
        return google.protobuf.wrappers_pb2.BoolValue(
            value=await project_service.check_user_joined_project(
                user_id=UUID(request.user_id),
                project_id=UUID(request.project_id),
            )
        )
