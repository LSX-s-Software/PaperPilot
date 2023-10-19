import uuid

from paperpilot_common.exceptions import ApiException
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


project_service: ProjectService = ProjectService()
