from typing import Any

from django.utils import timezone
from rest_framework.mixins import ListModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class APIRootViewSet(ListModelMixin, GenericViewSet):
    """
    API root view.
    """

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        time = timezone.localtime().isoformat()

        if user.is_anonymous:
            return Response(
                dict(
                    user=None,
                    time=time,
                )
            )
        else:
            return Response(
                dict(
                    user=self.handle_user_info(user),
                    time=time,
                )
            )

    def handle_user_info(self, user) -> dict:
        """
        处理用户信息
        :param user: 用户对象
        :return: 返回用户信息
        """
        return dict(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )
