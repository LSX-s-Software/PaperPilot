from django.contrib.auth.models import AbstractUser as DjangoAbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class AbstractUser(DjangoAbstractUser):
    """
    基本用户表
    """

    # 默认字段 - 基本信息
    username = models.CharField(
        "用户名",
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    password = models.CharField("密码", max_length=128)
    email = models.EmailField("邮箱", blank=True)

    # 默认字段 - 权限
    is_staff = models.BooleanField("工作人员", default=False)
    is_active = models.BooleanField("是否激活", default=True)
    is_superuser = models.BooleanField("超级用户", default=False)

    # 自定义字段
    # openid = models.CharField(
    #     max_length=64, unique=True, verbose_name="微信openid"
    # )

    avatar = models.ImageField(upload_to="avatar", default=r"avatar\default.jpg", verbose_name="头像")

    phone = models.CharField(max_length=13, default="", verbose_name="手机")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    # 禁用的默认字段
    first_name = None
    last_name = None
    date_joined = None
    last_login = None

    def __str__(self):
        return self.username

    class Meta:
        abstract = True
        db_table = "zq_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        ordering = ["-id"]
