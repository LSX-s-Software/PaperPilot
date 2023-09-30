# 重写 jwt 相关验证类
from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings

from paperpilot_common.exceptions import ApiException
from paperpilot_common.response import ResponseType


class ActiveUserAuthentication(JWTAuthentication):
    """
    激活用户认证类
    """

    AuthUser = get_user_model()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user_model = self.AuthUser

    def get_user(self, validated_token: Dict[str, Any]) -> Optional[AuthUser]:
        """
        Attempts to find and return a user using the given validated token.
        """
        # 获取用户 ID
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise ApiException(ResponseType.TokenInvalid, "token获取失败", record=True)  # token 不存在, 认证失败

        # 获取用户模型
        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise ApiException(ResponseType.ResourceNotFound, "用户不存在", record=True)  # 用户不存在, 认证失败

        self.check_activate(user)  # 检查用户激活类型

        return user

    @staticmethod
    def check_activate(user: AuthUser) -> None:
        """
        检查是否激活
        """
        if not user.is_active:
            raise ApiException(ResponseType.NotActive, "您的账号未激活，请完善个人信息后重试")


class NormalUserAuthentication(ActiveUserAuthentication):
    """
    无需激活的用户认证类
    """

    AuthUser = get_user_model()

    @staticmethod
    def check_activate(user: AuthUser) -> None:
        pass
