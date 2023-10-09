from typing import TYPE_CHECKING, Any

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from paperpilot_common.exceptions import ApiException
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.auth.serializers import OpenIdLoginSerializer, PasswordLoginSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request

AuthUser = get_user_model()


class OpenIdLoginView(TokenObtainPairView):
    """
    open id 登录视图（仅供测试微信登录使用）
    """

    queryset = AuthUser.objects.all()
    serializer_class = OpenIdLoginSerializer

    def post(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        """
        增加 post 方法, 支持 open id 登录
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            raise ApiException(
                ResponseType.ThirdLoginFailed,
                msg="微信登录失败",
                detail="生成token时simple jwt发生TokenError",
                record=True,
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class PasswordLoginView(TokenObtainPairView):
    """
    密码登录视图
    """

    serializer_class = PasswordLoginSerializer
