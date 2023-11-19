import uuid

from paperpilot_common.exceptions import ApiException
from paperpilot_common.protobuf.im.im_pb2 import (
    CreateWorkGroupRequest,
    DeleteWorkGroupRequest,
    InviteUserToGroupRequest,
    RemoveUserFromGroupRequest,
    UpdateWorkGroupRequest,
)
from paperpilot_common.protobuf.project.project_pb2 import (
    ListProjectResponse,
    ProjectInfo,
)
from paperpilot_common.protobuf.user.user_pb2 import UserIdList
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger
from project.models import Project, UserProject
from project.utils import get_random_invite_code

from server.business.grpc import user_client
from server.business.grpc.im import im_client


class ProjectService:
    logger = get_logger("project.service")
    user_service = user_client

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

    async def _get_project_info(
        self, project: Project | uuid.UUID
    ) -> ProjectInfo:
        """
        获取项目信息

        :param project: 项目对象或项目ID
        """
        project = await self._get_project(project)

        members_id = []
        owner_id = None

        async for up in project.users.all():
            if up.is_owner:
                owner_id = up.user_id.hex
            members_id.append(up.user_id.hex)

        member_infos = await self.user_service.stub.GetUserInfos(
            UserIdList(ids=members_id)
        )

        return ProjectInfo(
            id=project.id.hex,
            name=project.name,
            description=project.description,
            invite_code=project.invite_code,
            owner_id=owner_id,
            members=member_infos.infos.values(),
        )

    async def get_project_info(
        self, user_id: uuid.UUID, project: uuid.UUID
    ) -> ProjectInfo:
        """
        获取项目信息

        :param user_id: 用户ID
        :param project: 项目ID
        :return: 项目信息
        """
        await self._check_user(user_id, project)

        self.logger.debug(f"get project info: {project}")
        return await self._get_project_info(project)

    # return await project_service.update_project(self.project.id, request)
    async def update_project(
        self, user_id: uuid.UUID, request: ProjectInfo
    ) -> ProjectInfo:
        """
        更新项目信息

        :param user_id: 用户ID
        :param request: 更新请求
        :return: 项目信息
        """
        if request.name == "":
            raise ApiException(
                ResponseType.ParamEmpty, msg="项目名称不能为空", record=True
            )

        await self._check_user(user_id, request.id)

        project = await self._get_project(request.id)

        self.logger.debug(f"update project info: {project}")

        if project.name != request.name:
            project.name = request.name

            # 更新im信息
            await im_client.stub.UpdateWorkGroup(
                UpdateWorkGroupRequest(
                    id=project.id.hex,
                    name=project.name,
                )
            )

        project.description = request.description

        await project.asave()

        return await self._get_project_info(project)

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

        queryset = Project.objects.filter(users__user_id=user_id)

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

        project_users = []
        project_infos = []
        user_ids = set()
        async for project in queryset.prefetch_related("users"):
            project_infos.append(
                ProjectInfo(
                    id=project.id.hex,
                    name=project.name,
                    description=project.description,
                    invite_code=project.invite_code,
                )
            )
            project_users.append(project.users.all())
            user_ids.update([up.user_id.hex for up in project.users.all()])

        user_infos = await self.user_service.stub.GetUserInfos(
            UserIdList(ids=user_ids)
        )

        for i in range(len(project_infos)):
            project_info = project_infos[i]
            members = []

            for up in project_users[i]:
                if up.is_owner:
                    project_info.owner_id = up.user_id.hex
                members.append(user_infos.infos[up.user_id.hex])

            project_info.members.extend(members)

        return ListProjectResponse(
            projects=project_infos,
            total=total,
            next_page=next_page,
        )

    async def create_project(
        self, user_id: uuid.UUID, name: str, description: str
    ) -> ProjectInfo:
        """
        创建项目

        :param user_id: 用户ID
        :param name: 项目名称
        :param description: 项目描述
        :return: 项目信息
        """
        if name == "":
            raise ApiException(
                ResponseType.ParamEmpty, msg="项目名称不能为空", record=True
            )

        project = await Project.objects.acreate(
            name=name,
            description=description,
            invite_code=get_random_invite_code(),
        )

        await UserProject.objects.acreate(
            user_id=user_id,
            project=project,
            is_owner=True,
        )

        # 创建im信息
        await im_client.stub.CreateWorkGroup(
            CreateWorkGroupRequest(
                id=project.id.hex,
                name=project.name,
                owner=user_id.hex,
            )
        )

        self.logger.debug(f"create project: {project}")
        return await self._get_project_info(project)

    async def delete_project(self, user_id: uuid.UUID, project_id: uuid.UUID):
        """
        删除项目

        :param user_id: 用户ID
        :param project_id: 项目ID
        """
        await self._check_owner(user_id, project_id)

        self.logger.debug(f"delete project: {project_id}")

        # 删除im信息
        await im_client.stub.DeleteWorkGroup(
            DeleteWorkGroupRequest(
                id=project_id.hex,
            )
        )

        await Project.objects.filter(id=project_id).adelete()

    # urls.py的调用：return await project_service.join_project(request.invite_code)
    async def join_project(
        self, user_id: uuid.UUID, invite_code: str
    ) -> ProjectInfo:
        """
        加入项目

        :param user_id: 用户ID
        :param invite_code: 邀请码
        """
        project = await Project.objects.filter(invite_code=invite_code).afirst()
        if project is None:
            raise ApiException(
                ResponseType.ResourceNotFound,
                msg="邀请码错误",
                detail="您的邀请码错误，请核对后重试",
            )

        self.logger.debug(f"join project: {project}")

        if await UserProject.objects.filter(
            user_id=user_id, project=project
        ).aexists():
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="用户已加入项目",
                detail="您已加入该项目",
                record=False,
            )

        await UserProject.objects.acreate(
            user_id=user_id,
            project=project,
            is_owner=False,
        )

        # 创建im信息
        await im_client.stub.InviteUserToGroup(
            InviteUserToGroupRequest(
                group_id=project.id.hex, user_id=user_id.hex
            )
        )

        return await self._get_project_info(project)

    # project_service.quit_project(request.id)
    async def quit_project(self, user_id: uuid.UUID, project_id: uuid.UUID):
        """
        退出项目

        :param user_id: 用户ID
        :param project_id: 项目ID
        """
        await self._check_user(user_id, project_id)

        self.logger.debug(f"quit project: {project_id}")

        up = await UserProject.objects.filter(
            user_id=user_id, project=project_id
        ).afirst()

        if up.is_owner:
            raise ApiException(
                ResponseType.PermissionDenied, msg="项目所有者不能退出项目", record=True
            )

        # 删除im信息
        await im_client.stub.RemoveUserFromGroup(
            RemoveUserFromGroupRequest(
                group_id=project_id.hex, user_id=user_id.hex
            )
        )

        await up.adelete()

    async def _check_user(
        self, user_id: uuid.UUID, project: Project | uuid.UUID | str
    ) -> None:
        """
        检查用户是否加入项目，抛出异常

        :param user_id: 用户ID
        :param project: 项目对象或项目ID
        """
        project_id = project.id if isinstance(project, Project) else project
        project_id = (
            uuid.UUID(project_id) if isinstance(project_id, str) else project_id
        )

        if not await UserProject.objects.filter(
            user_id=user_id, project_id=project_id
        ).aexists():
            raise ApiException(
                ResponseType.PermissionDenied, msg="用户未加入项目", record=True
            )

    async def _check_owner(
        self, user_id: uuid.UUID, project: Project | uuid.UUID | str
    ) -> None:
        """
        检查用户是否为项目所有者，抛出异常

        :param user_id: 用户ID
        :param project: 项目对象或项目ID
        """
        # 获取uuid格式的project id
        project_id = project.id if isinstance(project, Project) else project
        project_id = (
            uuid.UUID(project_id) if isinstance(project_id, str) else project_id
        )

        if not await UserProject.objects.filter(
            user_id=user_id, project_id=project_id, is_owner=True
        ).aexists():
            raise ApiException(
                ResponseType.PermissionDenied, msg="用户不是项目所有者", record=True
            )

    async def check_user_joined_project(
        self, user_id: uuid.UUID, project_id: uuid.UUID
    ) -> bool:
        """
        检查用户是否加入项目

        :param user_id: 用户ID
        :param project_id: 项目对象或项目ID
        """
        self.logger.debug(f"check user {user_id} joined project: {project_id}")
        return await UserProject.objects.filter(
            user_id=user_id, project_id=project_id
        ).aexists()


project_service: ProjectService = ProjectService()
