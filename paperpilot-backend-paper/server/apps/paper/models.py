import uuid

from django.db import models


class Paper(models.Model):
    """
    论文
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="论文ID",
    )
    project_id = models.UUIDField(
        blank=False, verbose_name="项目ID", db_index=True
    )

    title = models.CharField(max_length=255, verbose_name="标题")
    abstract = models.TextField(verbose_name="摘要")
    keywords = models.JSONField(default=list, verbose_name="关键词列表")
    authors = models.JSONField(default=list, verbose_name="作者列表")

    tags = models.JSONField(default=list, verbose_name="标签列表")

    publication_year = models.IntegerField(default=0, verbose_name="出版年份")
    publication = models.CharField(max_length=255, verbose_name="出版方")
    event = models.CharField(max_length=255, verbose_name="会议/期刊")
    volume = models.CharField(max_length=255, verbose_name="卷")
    issue = models.CharField(max_length=255, verbose_name="期")
    pages = models.CharField(max_length=255, verbose_name="页码")

    doi = models.CharField(max_length=255, verbose_name="DOI")
    url = models.CharField(max_length=255, verbose_name="URL")

    FILE_PATH = "paper"
    file = models.FileField(upload_to=FILE_PATH, verbose_name="文件")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "pp_paper"
        verbose_name = "论文"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]

    def __repr__(self):
        return f"<Paper {self.title}>"

    def __str__(self):
        return self.title
