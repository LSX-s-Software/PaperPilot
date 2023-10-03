import unicodedata
import uuid

from django.contrib.auth.hashers import (
    check_password,
    is_password_usable,
    make_password,
)
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from paperpilot_common.utils.log import get_logger

from .regex import PHONE_REG, USERNAME_REG


class UserManager(models.Manager):
    use_in_migrations = True
    logger = get_logger("model.user_manager")

    async def _create_user(
        self, username: str, password: str, phone: str, **extra_fields
    ) -> "User":
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        username = self.model.normalize_username(username)
        user = self.model(
            username=username,
            phone=phone,
            last_login=timezone.now(),
            **extra_fields,
        )
        user.set_password(password)
        self.logger.info(f"create user: {user}")
        await user.asave(using=self._db)
        return user

    async def create_user(
        self, username: str, password: str, phone: str
    ) -> "User":
        return await self._create_user(
            username=username, password=password, phone=phone
        )


class User(models.Model):
    logger = get_logger("model.user")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="用户ID",
    )
    username = models.CharField(
        max_length=32,
        validators=[
            RegexValidator(
                regex=USERNAME_REG,
                message="用户名仅支持字母、数字、_、-，长度为2-16位",
            ),
        ],
        unique=True,
        verbose_name="用户名",
    )
    password = models.CharField(max_length=128, verbose_name="密码")
    phone = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=PHONE_REG,
                message="手机号格式错误",
            ),
        ],
        unique=True,
        verbose_name="手机号",
    )
    AVATAR_PATH = "user/avatar"
    avatar = models.FileField(
        upload_to=AVATAR_PATH,
        default=f"{AVATAR_PATH}/default.jpg",
        verbose_name="头像",
    )

    last_login = models.DateTimeField(verbose_name="最后登录时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    objects = UserManager()

    class Meta:
        db_table = "pp_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]

    def __repr__(self):
        return f"<User {self.username}>"

    def __str__(self):
        return self.username

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        return check_password(raw_password, self.password)

    def set_unusable_password(self) -> None:
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self) -> bool:
        """
        Return False if set_unusable_password() has been called for this user.
        """
        return is_password_usable(self.password)

    @classmethod
    def normalize_username(cls, username):
        """
        获取标准化的用户名
        """
        return (
            unicodedata.normalize("NFKC", username)
            if isinstance(username, str)
            else username
        )

    async def update_login_time(self):
        """
        更新登录时间
        """
        self.last_login = timezone.now()
        self.logger.debug(f"update login time: {self.last_login}")
        await self.asave(update_fields=["last_login"])
