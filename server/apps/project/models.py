import uuid

from django.db import models


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
        related_name="users",
    )
    is_owner = models.BooleanField(default=False, verbose_name="是否为所有者")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "pp_user_project"
        verbose_name = "用户项目"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]

    def __repr__(self):
        return f"<UserProject {self.user_id}-{self.project}>"

    def __str__(self):
        return f"{self.user_id}-{self.project}"
