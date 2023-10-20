import uuid

from paperpilot_common.exceptions import ApiException
from paperpilot_common.protobuf.project.project_pb2 import (
    ListProjectResponse,
    ProjectInfo,
)
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger
from project.models import Project


class ProjectService:
    logger = get_logger("project.service")

    async def _get_project(self, project: Project | uuid.UUID | str) -> Project:
        """
        获取项目对象

        :param project: 项目对象或项目ID
        :return: 项目对象
        """
        if isinstance(project, str):  # 转换为uuid
            project = uuid.UUID(project)

        if isinstance(project, uuid.UUID):  # 转换为项目对象
            project = await Project.objects.filter(id=project).afirst()
            if project is None:
                raise ApiException(
                    ResponseType.ResourceNotFound, msg="项目不存在", record=True
                )

        return project

    async def get_project_info(
        self, project: Project | uuid.UUID | str
    ) -> ProjectInfo:
        """
        获取项目信息

        :param project: 项目对象或项目ID
        :return: 项目信息
        """
        project = await self._get_project(project)

        self.logger.debug(f"get project info: {project}")
        return ProjectInfo(
            id=project.id.hex,
            name=project.name,
            description=project.description,
            invite_code=project.invite_code,
        )

    async def update_project(
        self, project: Project | uuid.UUID | str
    ) -> ProjectInfo:
        """
        更新项目信息

        :param project: 项目对象或项目ID
        :return: 项目信息
        """
        project = await self._get_project(project)

        self.logger.debug(f"update project info: {project}")
        return ProjectInfo(
            id=project.id.hex,
            name=project.name,
            description=project.description,
            invite_code=project.invite_code,
        )

    async def list_user_joined_projects(
        self, user: User | uuid.UUID | str
    ) -> ListProjectResponse:
        """
        获取用户参与的项目列表

        :param user: 用户对象或用户ID
        :return: 项目列表
        """
        user = await self._get_user(user)

        self.logger.debug(f"list user joined projects: {user}")
        projects = await user.projects.all()
        return ListProjectResponse(
            projects=[
                ProjectInfo(
                    id=project.id.hex,
                    name=project.name,
                    description=project.description,
                    invite_code=project.invite_code,
                )
                for project in projects
            ]
        )

    async def create_project(
        self, name: str, description: str, invite_code: str
    ) -> ProjectInfo:
        """
        创建项目

        :param name: 项目名称
        :param description: 项目描述
        :param invite_code: 邀请码
        :return: 项目信息
        """
        project = await Project.objects.create_project(
            name, description, invite_code
        )
        self.logger.debug(f"create project: {project}")
        return ProjectInfo(
            id=project.id.hex,
            name=project.name,
            description=project.description,
            invite_code=project.invite_code,
        )


project_service: ProjectService = ProjectService()
