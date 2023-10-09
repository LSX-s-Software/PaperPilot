# backend 用于用户验证
# 由于项目不使用django认证权限管理，backend不通过django的认证模块调用
# https://docs.djangoproject.com/zh-hans/4.1/topics/auth/customizing/

from typing import Any, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from rest_framework.request import Request

from paperpilot_common.utils.auth.exceptions import OpenIdNotBound, OpenIdNotProvided


class OpenIdBackend(BaseBackend):
    """
    OpenID 验证模块(获取token时调用)
    """

    AuthUser = get_user_model()

    openid_field: str = getattr(settings, "OPENID_FIELD", "openid")  # 获取 openid 字段名

    def __init__(self, auth_user_model=None):
        super().__init__()
        if auth_user_model:
            self.AuthUser = auth_user_model

    def authenticate(
        self,
        request: Optional[Request] = None,
        raise_exception: bool = False,
        **kwargs: Any,
    ) -> Optional[AuthUser]:
        """
        重写认证方法

        :param raise_exception: 是否产生异常，若为否则兼容django认证模块

        :param request: 传入请求


        :param kwargs: 字典参数

        :return: openid 对应用户对象
        """
        openid = kwargs.get(self.openid_field, None)

        try:
            # 未传入openid 认证失败
            if openid is None:
                raise OpenIdNotProvided
            # 获取 openid 对应用户
            try:
                return self.AuthUser.objects.get(**{self.openid_field: openid})
            except self.AuthUser.DoesNotExist:
                raise OpenIdNotBound(openid)
        except (OpenIdNotProvided, OpenIdNotBound) as e:
            if raise_exception:
                raise e
            return None

    def get_user(self, user_id: int) -> Optional[AuthUser]:
        """
        重写用户获取方法

        :param user_id: uid

        :return: 用户对象
        """
        try:
            user = self.AuthUser.objects.get(pk=user_id)
        except self.AuthUser.DoesNotExist:  # 用户不存在, 返回 None
            return None
        return user
