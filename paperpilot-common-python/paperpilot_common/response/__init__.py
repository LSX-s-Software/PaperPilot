from dataclasses import dataclass
from enum import Enum, unique
from typing import TYPE_CHECKING, Optional

import grpc
from django.http import JsonResponse

if TYPE_CHECKING:
    from paperpilot_common.exceptions import ApiException
    from paperpilot_common.response.types import JSONVal, ResponseData


class ResponseTypeEnum(Enum):
    @property
    def code(self) -> str:
        """
        根据枚举名称取状态码code

        :return: 状态码code
        """
        return self.value[0]

    @property
    def detail(self) -> str:
        """
        根据枚举名称取状态说明message

        :return: 状态说明message
        """
        return self.value[1]

    @property
    def status_code(self) -> int:
        """
        根据枚举名称取状态码status_code

        :return: 状态码status_code
        """
        return self.value[2]

    @property
    def grpc_status_code(self) -> grpc.StatusCode:
        """
        根据枚举名称取状态码grpc_status_code

        :return: 状态码grpc_status_code
        """
        return self.value[3]


# region ResponseType
@unique
class ResponseType(ResponseTypeEnum):
    """API状态类型"""

    Success = ("00000", "", 200, grpc.StatusCode.OK)
    ClientError = ("A0000", "用户端错误", 400, grpc.StatusCode.FAILED_PRECONDITION)
    LoginFailed = ("A0210", "用户登录失败", 400, grpc.StatusCode.INVALID_ARGUMENT)
    UsernameNotExist = ("A0211", "用户名不存在", 400, grpc.StatusCode.INVALID_ARGUMENT)
    PasswordWrong = ("A0212", "用户密码错误", 400, grpc.StatusCode.INVALID_ARGUMENT)
    LoginFailedExceed = ("A0213", "用户输入密码次数超限", 400, grpc.StatusCode.OUT_OF_RANGE)
    PhoneNotExist = ("A0214", "手机号不存在", 400, grpc.StatusCode.INVALID_ARGUMENT)
    LoginExpired = ("A0220", "用户登录已过期", 401, grpc.StatusCode.UNAUTHENTICATED)
    TokenInvalid = ("A0221", "token 无效", 401, grpc.StatusCode.UNAUTHENTICATED)
    TokenExpired = ("A0222", "token 过期", 401, grpc.StatusCode.UNAUTHENTICATED)
    RefreshTokenInvalid = ("A0222", "refresh token 无效", 401, grpc.StatusCode.UNAUTHENTICATED)
    RefreshTokenExpired = ("A0223", "refresh token 过期", 401, grpc.StatusCode.UNAUTHENTICATED)
    ThirdLoginFailed = ("A0230", "用户第三方登录失败", 401, grpc.StatusCode.UNAUTHENTICATED)
    ThirdLoginCaptchaError = ("A0232", "用户第三方登录验证码错误", 401, grpc.StatusCode.INVALID_ARGUMENT)
    ThirdLoginExpired = ("A0233", "用户第三方登录已过期", 401, grpc.StatusCode.UNAUTHENTICATED)
    PermissionError = ("A0300", "用户权限异常", 403, grpc.StatusCode.PERMISSION_DENIED)
    NotLogin = ("A0310", "用户未登录", 401, grpc.StatusCode.UNAUTHENTICATED)
    NotActive = ("A0311", "用户未激活", 403, grpc.StatusCode.PERMISSION_DENIED)
    PermissionDenied = ("A0312", "用户无权限", 403, grpc.StatusCode.PERMISSION_DENIED)
    ServiceNotAvailable = ("A0313", "不在服务时段", 403, grpc.StatusCode.PERMISSION_DENIED)
    UserBlocked = ("A0320", "黑名单用户", 403, grpc.StatusCode.PERMISSION_DENIED)
    UserFrozen = ("A0321", "账号被冻结", 403, grpc.StatusCode.PERMISSION_DENIED)
    IPInvalid = ("A0322", "非法 IP 地址", 401, grpc.StatusCode.UNAUTHENTICATED)
    ParamError = ("A0400", "用户请求参数错误", 400, grpc.StatusCode.INVALID_ARGUMENT)
    JSONParseFailed = ("A0410", "请求 JSON 解析错误", 400, grpc.StatusCode.INVALID_ARGUMENT)
    ParamEmpty = ("A0420", "请求必填参数为空", 400, grpc.StatusCode.INVALID_ARGUMENT)
    ParamValidationFailed = ("A0430", "请求参数值校验失败", 400, grpc.StatusCode.INVALID_ARGUMENT)
    RequestError = ("A0500", "用户请求服务异常", 400, grpc.StatusCode.INVALID_ARGUMENT)
    APINotFound = ("A0510", "请求接口不存在", 404, grpc.StatusCode.NOT_FOUND)
    MethodNotAllowed = ("A0511", "请求方法不允许", 405, grpc.StatusCode.NOT_FOUND)
    APIThrottled = ("A0512", "请求次数超出限制", 429, grpc.StatusCode.RESOURCE_EXHAUSTED)
    HeaderNotAcceptable = ("A0513", "请求头无法满足", 406, grpc.StatusCode.INVALID_ARGUMENT)
    ResourceNotFound = ("A0514", "请求资源不存在", 404, grpc.StatusCode.NOT_FOUND)
    Unimplemented = ("A0515", "接口未实现", 501, grpc.StatusCode.UNIMPLEMENTED)
    UploadError = ("A0600", "用户上传文件异常", 400, grpc.StatusCode.INVALID_ARGUMENT)
    UnsupportedMediaType = ("A0610", "用户上传文件类型不支持", 400, grpc.StatusCode.INVALID_ARGUMENT)
    UnsupportedMediaSize = ("A0613", "用户上传文件大小错误", 400, grpc.StatusCode.INVALID_ARGUMENT)
    VersionError = ("A0700", "用户版本异常", 400, grpc.StatusCode.INVALID_ARGUMENT)
    AppVersionError = ("A0710", "用户应用安装版本不匹配", 400, grpc.StatusCode.INVALID_ARGUMENT)
    APIVersionError = ("A0720", "用户 API 请求版本不匹配", 400, grpc.StatusCode.INVALID_ARGUMENT)
    ServerError = ("B0000", "系统执行出错", 500, grpc.StatusCode.INTERNAL)
    ServerTimeout = ("B0100", "系统执行超时", 500, grpc.StatusCode.DEADLINE_EXCEEDED)
    ServerResourceError = ("B0200", "系统资源异常", 500, grpc.StatusCode.INTERNAL)
    ThirdServiceError = ("C0000", "调用第三方服务出错", 500, grpc.StatusCode.INTERNAL)
    MiddlewareError = ("C0100", "中间件服务出错", 500, grpc.StatusCode.INTERNAL)
    ThirdServiceTimeoutError = ("C0200", "第三方系统执行超时", 500, grpc.StatusCode.DEADLINE_EXCEEDED)
    DatabaseError = ("C0300", "数据库服务出错", 500, grpc.StatusCode.INTERNAL)
    CacheError = ("C0400", "缓存服务出错", 500, grpc.StatusCode.INTERNAL)
    NotificationError = ("C0500", "通知服务出错", 500, grpc.StatusCode.INTERNAL)


# endregion


@dataclass
class ApiResponse:
    """API响应数据结构"""

    status_code: int
    code: str
    detail: str
    msg: str
    data: "ResponseData"

    def __init__(
        self,
        response_type: ResponseType = ResponseType.Success,
        data: "JSONVal" = "",
        msg: Optional[str] = None,
        ex: Optional["ApiException"] = None,
    ):
        """
        Api 响应
        :param response_type: 响应类型
        :param data: 响应数据
        :param msg: 面向用户的响应消息
        :param ex: Api异常(用于获取相关数据)
        """
        if ex:  # 优先使用异常
            response_type = ex.response_type  # 获取传入异常的类型
            msg = ex.msg  # 获取传入异常的消息

        self.status_code = response_type.status_code
        self.code = response_type.code
        self.detail = response_type.detail
        self.msg = msg if msg else self.detail
        self.data = data

    def __str__(self) -> str:
        return f"code: {self.code}, detail: {self.detail}, msg: {self.msg}, data: {self.data}"

    def __dict__(self) -> "ResponseData":
        return {
            "code": self.code,
            "detail": self.detail,
            "msg": self.msg,
            "data": self.data,
        }

    def to_json_response(self) -> JsonResponse:
        return JsonResponse(self.__dict__(), status=self.status_code)
