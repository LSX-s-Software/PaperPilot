import uuid

from django.db import models
from paperpilot_common.utils.log import get_logger


class ProjectManager(models.Manager):
    use_in_migrations = True
    logger = get_logger("model.project_manager")

    async def _create_project(
        self, name: str, description: str, invite_code: str
    ) -> "Project":
        """
        创建项目
        """
        project = self.model(
            name=name,
            description=description,
            invite_code=invite_code,
        )
        self.logger.info(f"create project: {project}")
        await project.asave(using=self._db)
        return project

    async def create_project(
        self, name: str, description: str, invite_code: str
    ) -> "Project":
        return await self._create_project(
            name=name, description=description, invite_code=invite_code
        )


class Project(models.Model):
    """
    项目
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="项目ID",
    )
    name = models.CharField(max_length=64, verbose_name="项目名称")
    description = models.TextField(blank=True, verbose_name="项目描述")
    invite_code = models.CharField(max_length=64, verbose_name="邀请码")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "pp_project"
        verbose_name = "项目"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]

    def __repr__(self):
        return f"<Project {self.name}>"

    def __str__(self):
        return self.name


class UserProject(models.Model):
    """
    用户项目关联表
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID"
    )
    user_id = models.UUIDField(blank=False, verbose_name="用户ID", db_index=True)
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE,
        verbose_name="项目",
        db_index=True,
    )
    is_owner = models.BooleanField(default=False, verbose_name="是否为所有者")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "pp_user_project"
        verbose_name = "用户项目"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "project"],
                condition=models.Q(is_active=True),
                name="user_and_project_uniq",
            )
        ]

    def __repr__(self):
        return f"<UserProject {self.user_id}-{self.project}>"

    def __str__(self):
        return f"{self.user_id}-{self.project}"
