import hashlib
import random
import time
import traceback
from datetime import datetime
from sys import exc_info
from typing import TYPE_CHECKING, Optional

from django.conf import settings
from django.utils.timezone import now

from paperpilot_common.protobuf.common import exce_pb2
from paperpilot_common.response.utils import get_response_type

if TYPE_CHECKING:
    from paperpilot_common.exceptions.types import ExceptionData, ExceptionInfo
    from paperpilot_common.response import ResponseData, ResponseType


class ApiException(Exception):
    """API异常"""

    DEFAULT_MSG = "服务器开小差了"
    RECORD_MSG_TEMPLATE = "请向工作人员反馈以下内容："

    record: bool
    response_type: "ResponseType"
    eid: Optional[str]
    detail: str
    msg: str
    event_id: Optional[str]
    inner: Optional[Exception]
    _exc_data: Optional["ExceptionInfo"]
    time: datetime

    def __init__(
        self,
        type: "ResponseType",
        msg: Optional[str] = None,
        inner: Optional[Exception] = None,
        record: Optional[bool] = None,
        detail: Optional[str] = None,
    ) -> None:
        """
        API异常
        :param type: 异常类型
        :param msg: 异常建议(面向用户)
        :param inner: 内部异常
        :param record: 是否记录异常
        :param detail: 异常详情(面向开发者)
        """
        self.record = record if record is not None else type.status_code == 500  # 是否记录异常

        self.response_type: "ResponseType" = type
        if self.record:  # 记录异常
            self.eid = self.get_exp_id()  # 异常id
        else:
            self.eid = None
        self.detail = self.get_exp_detail(detail)  # 异常详情
        self.msg = self.get_exp_msg(msg)  # 异常用户提示
        self.event_id = None

        super().__init__(self.detail)

        self.inner = inner
        self._exc_data = None
        self.time = now()

    def get_exp_detail(self, detail: Optional[str]) -> str:
        """
        获取异常详情(面向开发者)
        :param detail: 自定义异常详情
        :return: 异常详情
        """
        res = detail or self.response_type.detail  # 获取异常详情
        if self.record:  # 记录异常
            res = f"{res}, {self.eid}"  # 将自定义异常详情添加到末尾
        return res

    def get_exp_msg(self, msg: Optional[str]) -> str:
        """
        获取异常用户提示(面向用户)
        :param msg: 自定义异常用户提示
        :return: 异常用户提示
        """
        if self.record:  # 记录异常
            if msg:  # 如果有自定义异常用户提示
                res = f"{msg}，{self.RECORD_MSG_TEMPLATE}{self.eid}"  # 使用自定义用户提示
            else:
                res = f"{self.DEFAULT_MSG}，{self.RECORD_MSG_TEMPLATE}{self.eid}"  # 标准用户提示
        else:  # 不记录异常
            res = msg or self.response_type.detail  # 获取异常详情
        return res

    @property
    def exc_data(self) -> "ExceptionInfo":
        if self._exc_data is None:
            self._exc_data = self.get_exception_info()
        return self._exc_data

    @exc_data.setter
    def exc_data(self, value: "ExceptionInfo") -> None:
        self._exc_data = value

    @property
    def response_data(self) -> "ResponseData":
        """
        获取响应数据
        :return: 响应数据
        """
        return {
            "code": self.response_type.code,
            "detail": self.detail,
            "msg": self.msg,
            "data": self.exception_data,
        }

    @staticmethod
    def get_exp_id() -> str:
        """
        获取异常id
        :return: 异常id
        """
        sha = hashlib.sha1()
        exp_id = time.strftime("%Y%m%d%H%M%S") + "_%04d" % random.randint(0, 10000)
        sha.update(exp_id.encode("utf-8"))
        return sha.hexdigest()[:6]

    def get_exception_info(self) -> "ExceptionInfo":
        """
        获取异常信息
        :return: 异常信息
        """
        exc_type, exc_value, exc_traceback_obj = exc_info()
        info: "ExceptionInfo" = {
            "type": str(exc_type),
            "value": str(exc_value),
            "traceback": traceback.format_stack(),
            "inner_type": None,
            "inner_value": None,
        }

        if self.inner:
            info["inner_type"] = str(type(self.inner))
            info["inner_value"] = str(self.inner)

        return info

    @property
    def exception_data(self) -> "ExceptionData":
        """
        获取异常返回数据
        :return: 返回数据
        """
        data: "ExceptionData" = {
            "eid": self.eid,
            "sentry_id": self.event_id,
            "time": self.time,
            "info": None,
        }

        if settings.DEBUG:
            data["info"] = self.exc_data

        return data

    @classmethod
    def from_protos(cls, pb: "exce_pb2.ApiException") -> "ApiException":
        """
        从grpc protos创建异常
        :param pb: grpc protos
        :return: 异常
        """

        exc = cls(
            type=get_response_type(pb.code),
            msg=pb.detail,
            record=(pb.data.sentry_id is not None),
            detail=pb.message,
        )
