import collections.abc
import typing

import google.protobuf
import google.protobuf.empty_pb2
import google.protobuf.wrappers_pb2
import paperpilot_common.protobuf
import paperpilot_common.protobuf.project.project_pb2
from paperpilot_common.middleware.server.auth import AuthMixin
from paperpilot_common.protobuf.project import project_pb2_grpc
from paperpilot_common.utils.types import _ServicerContext

from .services import project_service


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
        return await project_service.list_user_joined_projects(self.request.id)
        # pass

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
        return await project_service.get_project_info(request.id)
        # pass

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
            request.name, request.description, request.invite_code
        )
        # pass

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
        return await project_service.update_project(request.id)
        # pass

    async def DeleteProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ProjectId,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        return await project_service.delete_project(self.project.id)
        pass

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
        return await project_service.join_project(request.invite_code)
        pass

    async def QuitProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.ProjectId,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.empty_pb2.Empty,
        collections.abc.Awaitable[google.protobuf.empty_pb2.Empty],
    ]:
        return await project_service.quit_project(self.project.id)
        pass


class ProjectController(project_pb2_grpc.ProjectServiceServicer):
    async def CheckUserJoinedProject(
        self,
        request: paperpilot_common.protobuf.project.project_pb2.CheckUserJoinedProjectRequest,
        context: _ServicerContext,
    ) -> typing.Union[
        google.protobuf.wrappers_pb2.BoolValue,
        collections.abc.Awaitable[google.protobuf.wrappers_pb2.BoolValue],
    ]:
        return await project_service.check_user_joined_project(
            request.user_id, request.project_id
        )
        pass
