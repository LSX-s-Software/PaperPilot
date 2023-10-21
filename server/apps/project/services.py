import uuid

from django.contrib.auth.models import User
from paperpilot_common.exceptions import ApiException
from paperpilot_common.protobuf.project.project_pb2 import (
    ListProjectResponse,
    ProjectInfo,
)
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger
from project.models import Project, UserProject

from server.business.grpc import user_client


class ProjectService:
    logger = get_logger("project.service")
    user_service = user_client.stub

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

    # return await project_service.update_project(self.project.id, request)
    async def update_project(
        self, project: Project | uuid.UUID | str, request
    ) -> ProjectInfo:
        """
        更新项目信息

        :param project: 项目对象或项目ID
        :param request: 更新请求
        :return: 项目信息
        """
        project = await self._get_project(project)

        self.logger.debug(f"update project info: {project}")

        project.name = request.name
        project.description = request.description
        project.invite_code = request.invite_code

        await project.asave()

        return ProjectInfo(
            id=project.id.hex,
            name=project.name,
            description=project.description,
            invite_code=project.invite_code,
        )

    async def list_user_joined_projects(
        self, user_id: uuid.UUID, page: int, page_size: int, order_by: str
    ) -> ListProjectResponse:
        """
        获取用户参与的项目列表

        :param user_id: 用户ID
        :param page: 页码
        :param page_size: 每页大小
        :param order_by: 排序字段
        :return: 项目列表
        """
        self.logger.debug(f"list user joined projects: {user_id}")

        # 获取所有与用户关联的UserProject对象
        user_projects = UserProject.objects.filter(user_id=user_id)

        # 获取所有与UserProject对象关联的项目
        queryset = Project.objects.filter(user_projects__in=user_projects)

        total = await queryset.acount()

        if total == 0:  # 无
            return ListProjectResponse(
                projects=[],
                total=0,
                next_page=0,
            )

        # 计算下一页
        next_page = page + 1 if page * page_size < total else 0

        # 排序
        queryset = queryset.order_by(order_by)

        # 分页
        queryset = queryset[(page - 1) * page_size : page * page_size]

        projects = []
        async for project in queryset:
            projects.append(
                ProjectInfo(
                    id=project.id.hex,
                    name=project.name,
                    description=project.description,
                    invite_code=project.invite_code,
                )
            )

        return ListProjectResponse(
            projects=projects,
            total=total,
            next_page=next_page,
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

    async def delete_project(self, project: Project | uuid.UUID | str):
        """
        删除项目

        :param project: 项目对象或项目ID
        """
        project = await self._get_project(project)

        self.logger.debug(f"delete project: {project}")
        await project.adelete()

    # urls.py的调用：return await project_service.join_project(request.invite_code)
    async def join_project(self, invite_code: str):
        """
        加入项目

        :param invite_code: 邀请码
        """
        project = await Project.objects.filter(invite_code=invite_code).afirst()
        if project is None:
            raise ApiException(
                ResponseType.ResourceNotFound, msg="项目不存在", record=True
            )

        self.logger.debug(f"join project: {project}")
        await self.user.projects.add(project)

    # project_service.quit_project(request.id)
    async def quit_project(self, project: Project | uuid.UUID | str):
        """
        退出项目

        :param project: 项目对象或项目ID
        """
        project = await self._get_project(project)

        self.logger.debug(f"quit project: {project}")
        await self.user.projects.remove(project)

    async def check_user_joined_project(
        self, user: User | uuid.UUID | str, project: Project | uuid.UUID | str
    ):
        """
        检查用户是否加入项目

        :param user: 用户对象或用户ID
        :param project: 项目对象或项目ID
        """
        user = await self._get_user(user)
        project = await self._get_project(project)

        self.logger.debug(f"check user joined project: {project}")
        return await user.projects.filter(id=project.id).exists()


project_service: ProjectService = ProjectService()
