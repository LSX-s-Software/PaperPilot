from typing import Optional, Union

import django.core.exceptions as django_exceptions
import rest_framework.exceptions as drf_exceptions
import rest_framework_simplejwt.exceptions as jwt_exceptions
from django.http import Http404
from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.types import ExceptionHandlerContext
from rest_framework.response import Response
from rest_framework.views import set_rollback

from paperpilot_common.exceptions import ApiException
from paperpilot_common.exceptions.configs import zq_exception_settings
from paperpilot_common.exceptions.types import ExtraHeaders
from paperpilot_common.response import ResponseType
from paperpilot_common.response.types import ApiExceptionResponse

if zq_exception_settings.SENTRY_ENABLE:  # pragma: no cover
    import sentry_sdk


class ApiExceptionHandler:
    exc: Exception
    context: ExceptionHandlerContext

    def __init__(self, exc: Exception, context: ExceptionHandlerContext) -> None:
        self.exc = exc
        self.context = context

    def run(self) -> Optional[ApiExceptionResponse]:
        """
        处理异常
        :return: 响应数据或失败为None
        """
        exc = self.convert_known_exceptions(self.exc)  # 将django的异常转换为drf的异常

        if zq_exception_settings.EXCEPTION_UNKNOWN_HANDLE:  # 未知异常处理（非drf、api的异常）
            exc = self.convert_unhandled_exceptions(exc)  # 将未知异常转换为drf异常
        exc = self.convert_drf_exceptions(exc)  # 将drf异常转换为api异常
        set_rollback()  # 设置事务回滚
        response = None

        if isinstance(exc, ApiException):  # 如果是api异常则进行解析
            response = self.get_response(exc)
            if exc.record:  # 如果需要记录
                if zq_exception_settings.SENTRY_ENABLE:
                    self._notify_sentry(exc, response)
                # 将event_id写入响应数据
                response.data["data"]["event_id"] = exc.event_id
                # 将异常信息记录到response中，便于logger记录
                response.exception_data = exc

        return response

    def _notify_sentry(self, exc: ApiException, response: Response) -> None:
        """
        通知sentry, 可在notify_sentry中自定义其他内容
        :param exc: Api异常
        :param response: 响应数据
        :return: None
        """
        try:
            self.notify_sentry(exc, response)  # 调用自定义通知
        except Exception:
            pass

        # 默认异常汇报
        sentry_sdk.api.set_tag("exception_type", exc.response_type.name)
        sentry_sdk.set_context(
            "exp_info",
            {
                "eid": response.data["data"]["eid"],
                "code": response.data["code"],
                "detail": response.data["detail"],
                "msg": response.data["msg"],
            },
        )
        sentry_sdk.set_context("details", response.data["data"]["details"])
        exc.event_id = sentry_sdk.api.capture_exception(self.exc)  # 发送至sentry

    def notify_sentry(self, exc: ApiException, response: Response) -> None:
        """
        自定义sentry通知
        :param exc: Api异常
        :param response: 响应数据
        :return: None
        """
        user = self.context["request"].user
        if user.is_authenticated:
            sentry_sdk.api.set_tag("role", "user")
            sentry_sdk.api.set_user(
                {
                    "id": user.id,
                    "email": user.username,
                    "phone": user.phone if hasattr(user, "phone") else None,
                }
            )
        else:
            sentry_sdk.api.set_tag("role", "guest")

    def get_response(self, exc: ApiException) -> Response:
        """
        获取响应数据
        :param exc: Api异常
        :return:
        """
        headers = self.get_headers(exc.inner)
        data = exc.response_data

        info = None
        if exc.inner:
            if isinstance(exc.inner, drf_exceptions.APIException):
                info = ExceptionFormatter(exc.inner, self.context, self.exc).run()
            else:
                info = exc.inner.args[0] if exc.inner.args else None
        data["data"]["details"] = info

        return Response(
            data,
            status=exc.response_type.status_code,
            headers=headers,
        )

    @staticmethod
    def get_headers(exc: Exception) -> ExtraHeaders:
        """
        获取额外响应头
        :param exc: 异常
        :return: headers
        """
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait
        return headers

    @staticmethod
    def convert_known_exceptions(exc: Exception) -> Exception:
        """
        By default, Django's built-in `Http404` and `PermissionDenied` are converted
        to their DRF equivalent.
        """
        if isinstance(exc, Http404):
            return drf_exceptions.NotFound()
        elif isinstance(exc, django_exceptions.PermissionDenied):
            return drf_exceptions.PermissionDenied()
        # jwt
        elif isinstance(exc, jwt_exceptions.InvalidToken):
            return ApiException(
                type=ResponseType.TokenInvalid,
                inner=exc,
            )
        elif isinstance(exc, jwt_exceptions.AuthenticationFailed):
            return ApiException(
                type=ResponseType.LoginFailed,
                inner=exc,
            )
        elif isinstance(exc, jwt_exceptions.TokenError):
            return ApiException(
                type=ResponseType.TokenInvalid,
                detail="Token解析错误",
                inner=exc,
            )
        else:
            return exc

    @staticmethod
    def convert_unhandled_exceptions(
        exc: Exception,
    ) -> Union[drf_exceptions.APIException, ApiException]:
        """
        Any non-DRF unhandled exception is converted to an APIException which
        has a 500 status code.
        """
        if not isinstance(exc, drf_exceptions.APIException) and not isinstance(exc, ApiException):
            return drf_exceptions.APIException(detail=str(exc))
        else:
            return exc

    @staticmethod
    def convert_drf_exceptions(
        exc: Union[drf_exceptions.APIException, ApiException, Exception],
    ) -> ApiException | Exception:
        """
        转换drf异常
        :param exc: drf异常
        :return: ApiException
        """
        if isinstance(exc, ApiException):
            return exc
        # 处理drf异常
        record = False
        response_type = ResponseType.ServerError
        detail = None
        msg = None

        if isinstance(exc, drf_exceptions.ParseError):
            response_type = ResponseType.JSONParseFailed
        elif isinstance(exc, drf_exceptions.AuthenticationFailed):
            response_type = ResponseType.LoginFailed
        elif isinstance(exc, drf_exceptions.NotAuthenticated):
            # 未登录
            response_type = ResponseType.NotLogin
        elif isinstance(exc, drf_exceptions.PermissionDenied):
            response_type = ResponseType.PermissionDenied
        elif isinstance(exc, drf_exceptions.NotFound):
            response_type = ResponseType.APINotFound
        elif isinstance(exc, drf_exceptions.ValidationError):
            # 校验失败
            record = True
            response_type = ResponseType.ParamValidationFailed
        elif isinstance(exc, drf_exceptions.MethodNotAllowed):
            # 方法错误
            record = True
            response_type = ResponseType.MethodNotAllowed
            detail = f"不允许{getattr(exc, 'args', None)[0]}请求"
        elif isinstance(exc, drf_exceptions.NotAcceptable):
            record = True
            response_type = ResponseType.HeaderNotAcceptable
            detail = f"不支持{getattr(exc, 'args', None)[0]}的响应格式"
        elif isinstance(exc, drf_exceptions.UnsupportedMediaType):
            record = True
            response_type = ResponseType.UnsupportedMediaType
            detail = f"不支持{getattr(exc, 'args', None)[0]}的请求格式"
            msg = f"暂不支持{getattr(exc, 'args', None)[0]}文件上传，请使用支持的文件格式重试"
        elif isinstance(exc, drf_exceptions.Throttled):
            record = True
            response_type = ResponseType.APIThrottled
            detail = f"请求频率过高，请{getattr(exc, 'args', None)[0]}s后再试"
            msg = f"请求太快了，请{getattr(exc, 'args', None)[0]}s后再试"
        elif isinstance(exc, drf_exceptions.APIException):
            record = True
            response_type = ResponseType.ServerError
        else:
            # 不处理其他异常
            return exc

        return ApiException(response_type, msg, exc, record, detail)


def exception_handler(exc: Exception, context: ExceptionHandlerContext) -> Optional[ApiExceptionResponse]:
    """
    自定义异常处理

    :param exc: 异常
    :param context: 上下文
    :return: 处理程序
    """
    handler_class = zq_exception_settings.EXCEPTION_HANDLER_CLASS

    if handler_class != ApiExceptionHandler and not issubclass(handler_class, ApiExceptionHandler):
        raise ImportError(f"{handler_class} is not a subclass of ApiExceptionHandler")

    return handler_class(exc, context).run()
