from dataclasses import dataclass
from enum import Enum, unique
from typing import TYPE_CHECKING, Optional

from django.http import JsonResponse

if TYPE_CHECKING:
    from zq_django_util.exceptions import ApiException
    from zq_django_util.response.types import JSONVal, ResponseData


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


# region ResponseType
@unique
class ResponseType(ResponseTypeEnum):
    """API状态类型"""

    Success = ("00000", "", 200)
    ClientError = ("A0000", "用户端错误", 400)
    LoginFailed = ("A0210", "用户登录失败", 400)
    UsernameNotExist = ("A0211", "用户名不存在", 400)
    PasswordWrong = ("A0212", "用户密码错误", 400)
    LoginFailedExceed = ("A0213", "用户输入密码次数超限", 400)
    PhoneNotExist = ("A0214", "手机号不存在", 400)
    LoginExpired = ("A0220", "用户登录已过期", 401)
    TokenInvalid = ("A0221", "token 无效或已过期", 401)
    RefreshTokenInvalid = ("A0221", "refresh token 无效或已过期", 401)
    ThirdLoginFailed = ("A0230", "用户第三方登录失败", 401)
    ThirdLoginCaptchaError = ("A0232", "用户第三方登录验证码错误", 401)
    ThirdLoginExpired = ("A0233", "用户第三方登录已过期", 401)
    PermissionError = ("A0300", "用户权限异常", 403)
    NotLogin = ("A0310", "用户未登录", 401)
    NotActive = ("A0311", "用户未激活", 403)
    PermissionDenied = ("A0312", "用户无权限", 403)
    ServiceNotAvailable = ("A0313", "不在服务时段", 403)
    UserBlocked = ("A0320", "黑名单用户", 403)
    UserFrozen = ("A0321", "账号被冻结", 403)
    IPInvalid = ("A0322", "非法 IP 地址", 401)
    ParamError = ("A0400", "用户请求参数错误", 400)
    JSONParseFailed = ("A0410", "请求 JSON 解析错误", 400)
    ParamEmpty = ("A0420", "请求必填参数为空", 400)
    ParamValidationFailed = ("A0430", "请求参数值校验失败", 400)
    RequestError = ("A0500", "用户请求服务异常", 400)
    APINotFound = ("A0510", "请求接口不存在", 404)
    MethodNotAllowed = ("A0511", "请求方法不允许", 405)
    APIThrottled = ("A0512", "请求次数超出限制", 429)
    HeaderNotAcceptable = ("A0513", "请求头无法满足", 406)
    ResourceNotFound = ("A0514", "请求资源不存在", 404)
    UploadError = ("A0600", "用户上传文件异常", 400)
    UnsupportedMediaType = ("A0610", "用户上传文件类型不支持", 400)
    UnsupportedMediaSize = ("A0613", "用户上传文件大小错误", 400)
    VersionError = ("A0700", "用户版本异常", 400)
    AppVersionError = ("A0710", "用户应用安装版本不匹配", 400)
    APIVersionError = ("A0720", "用户 API 请求版本不匹配", 400)
    ServerError = ("B0000", "系统执行出错", 500)
    ServerTimeout = ("B0100", "系统执行超时", 500)
    ServerResourceError = ("B0200", "系统资源异常", 500)
    ThirdServiceError = ("C0000", "调用第三方服务出错", 500)
    MiddlewareError = ("C0100", "中间件服务出错", 500)
    ThirdServiceTimeoutError = ("C0200", "第三方系统执行超时", 500)
    DatabaseError = ("C0300", "数据库服务出错", 500)
    CacheError = ("C0400", "缓存服务出错", 500)
    NotificationError = ("C0500", "通知服务出错", 500)


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
