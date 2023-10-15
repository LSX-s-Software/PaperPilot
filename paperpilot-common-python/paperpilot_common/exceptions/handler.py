from google.protobuf import any_pb2
from google.rpc import status_pb2

from paperpilot_common.exceptions import ApiException
from paperpilot_common.exceptions.configs import zq_exception_settings
from paperpilot_common.helper.field import datetime_to_timestamp
from paperpilot_common.middleware.server.auth import get_user
from paperpilot_common.protobuf.common import exce_pb2
from paperpilot_common.response import ResponseType
from paperpilot_common.response.types import ResponseData
from paperpilot_common.utils.log import get_logger
from paperpilot_common.utils.singleton import Singleton

if zq_exception_settings.SENTRY_ENABLE:  # pragma: no cover
    import sentry_sdk


def map_exception_to_response_type(exception):
    from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
    from django.db import DatabaseError, IntegrityError
    from django.http import Http404
    from django.urls.exceptions import NoReverseMatch

    if isinstance(exception, ValidationError):
        # Django 验证错误，可以映射为参数错误的 ResponseType
        return ResponseType.ParamValidationFailed
    elif isinstance(exception, IntegrityError):
        # 数据库完整性错误，可以映射为数据库服务出错的 ResponseType
        return ResponseType.ParamValidationFailed
    elif isinstance(exception, DatabaseError):
        # 数据库错误，可以映射为数据库服务出错的 ResponseType
        return ResponseType.DatabaseError
    elif isinstance(exception, Http404):
        # HTTP 404 错误，可以映射为资源不存在的 ResponseType
        return ResponseType.ResourceNotFound
    elif isinstance(exception, ObjectDoesNotExist):
        # Django 对象不存在异常，可以映射为资源不存在的 ResponseType
        return ResponseType.ResourceNotFound
    elif isinstance(exception, NoReverseMatch):
        # Django URL 反向匹配异常，可以映射为请求接口不存在的 ResponseType
        return ResponseType.APINotFound
    elif isinstance(exception, PermissionDenied):
        # Django 权限拒绝异常，可以映射为用户无权限的 ResponseType
        return ResponseType.PermissionDenied
    elif isinstance(exception, ValueError):
        # 值错误异常，可以映射为参数错误的 ResponseType
        return ResponseType.ParamError
    elif isinstance(exception, KeyError):
        # 键错误异常，可以映射为参数错误的 ResponseType
        return ResponseType.ParamError
    elif isinstance(exception, FileNotFoundError):
        # 文件未找到异常，可以映射为资源不存在的 ResponseType
        return ResponseType.ResourceNotFound
    elif isinstance(exception, IOError):
        # 输入/输出异常，可以映射为服务器错误的 ResponseType
        return ResponseType.ServerError
    elif isinstance(exception, TypeError):
        # 类型错误异常，可以映射为参数错误的 ResponseType
        return ResponseType.ParamError
    elif isinstance(exception, AttributeError):
        # 属性错误异常，可以映射为参数错误的 ResponseType
        return ResponseType.ParamError
    elif isinstance(exception, NotImplementedError):
        # 未实现异常，可以映射为接口未实现的 ResponseType
        return ResponseType.Unimplemented
    elif isinstance(exception, Exception):
        # 其他异常，可以映射为服务器错误的 ResponseType
        return ResponseType.ServerError


class ApiExceptionHandler(metaclass=Singleton):
    logger = get_logger("server.interceptor.exception")

    def _convert(self, exc: Exception) -> ApiException:
        if not isinstance(exc, ApiException):
            self.logger.debug(f"convert exception {exc.__class__.__name__} to ApiException")
            response_type = map_exception_to_response_type(exc)
            exc = ApiException(response_type, inner=exc, detail=str(exc), record=True)

        return exc

    def notify_sentry(self, data: ResponseData, exc: ApiException) -> str:
        """
        通知sentry
        :param exc: Api异常
        :param data: 响应数据
        :return: sentry_id
        """
        user = get_user()
        if user.is_authenticated:
            sentry_sdk.api.set_tag("role", "user")
            sentry_sdk.api.set_user(
                {
                    "id": user.id,
                }
            )
        else:
            sentry_sdk.api.set_tag("role", "guest")

        # 默认异常汇报
        sentry_sdk.api.set_tag("exception_type", exc.response_type.name)
        sentry_sdk.set_context(
            "exp_info",
            {
                "eid": data["data"]["eid"],
                "code": data["code"],
                "detail": data["detail"],
                "msg": data["msg"],
            },
        )

        sentry_sdk.set_context(
            "details",
            data,
        )

        eid = sentry_sdk.api.capture_exception(exc.inner if exc.inner else exc)  # 优先发送内部错误
        self.logger.debug(f"notify sentry {eid}")

        return eid

    def grpc_handle(self, exc: Exception) -> status_pb2.Status:
        exc = self._convert(exc)
        response_data = exc.response_data

        if exc.record:  # 如果需要记录
            if zq_exception_settings.SENTRY_ENABLE:
                sentry_id = self.notify_sentry(response_data, exc)
                response_data["data"]["sentry_id"] = sentry_id

        protos = self.get_grpc_protos(response_data)

        detail = any_pb2.Any()
        detail.Pack(protos)

        return status_pb2.Status(
            code=exc.response_type.grpc_status_code.value[0],
            message=protos.detail,  # 面向开发者
            details=[detail],
        )

    def get_grpc_protos(self, response_data) -> exce_pb2.ApiException:
        """
        获取grpc protos
        :param response_data: 响应数据
        :return: grpc protos
        """
        if response_data["data"]["info"]:
            info = exce_pb2.ExceptionInfo(
                type=response_data["data"]["info"]["type"],
                value=response_data["data"]["info"]["value"],
                traceback=response_data["data"]["info"]["traceback"],
                inner_type=response_data["data"]["info"]["inner_type"],
                inner_value=response_data["data"]["info"]["inner_value"],
            )
        else:
            info = None

        return exce_pb2.ApiException(
            code=response_data["code"],
            detail=response_data["detail"],
            message=response_data["msg"],
            data=exce_pb2.ApiExceptionData(
                eid=response_data["data"]["eid"],
                sentry_id=response_data["data"]["sentry_id"],
                time=datetime_to_timestamp(response_data["data"]["time"]),
                info=info,
            ),
        )
