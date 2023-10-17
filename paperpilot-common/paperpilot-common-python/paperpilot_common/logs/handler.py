import base64
import json
import time
from logging import getLogger
from queue import Queue
from threading import Thread
from typing import Dict, List, Optional

from django.core.files.uploadedfile import UploadedFile
from django.db.utils import OperationalError
from django.urls import resolve
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.settings import api_settings

import paperpilot_common
from paperpilot_common.exceptions import ApiException
from paperpilot_common.logs.configs import drf_logger_settings
from paperpilot_common.logs.models import ExceptionLog, RequestLog
from paperpilot_common.logs.types import ExceptionLogDict, FileDataDict, RequestLogDict
from paperpilot_common.logs.utils import close_old_database_connections, get_client_ip, get_headers, mask_sensitive_data
from paperpilot_common.response.types import ApiExceptionResponse, JSONVal

logger = getLogger("drf_logger")


class HandleLogAsync(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag = True
        self._queue: Queue[(Request, Response, float, float)] = Queue(maxsize=drf_logger_settings.QUEUE_MAX_SIZE)

    def __enter__(self):
        self.daemon = True
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def run(self) -> None:
        """
        线程开始
        :return:
        """
        self.flag = True
        self.start_queue_process()

    def stop(self) -> None:
        """
        强制结束线程
        :return:
        """
        self.flag = False
        self.join()

    def prepare_request_log(
        self,
        request: Request,
        response: ApiExceptionResponse,
        start_time: float,
        end_time: float | None,
    ) -> Optional[RequestLogDict]:
        """
        处理请求日志
        :param request:
        :param response:
        :param start_time:
        :param end_time:
        :return:
        """
        # region 检查是否需要记录日志
        if not drf_logger_settings.DATABASE and not drf_logger_settings.SIGNAL:
            return

        url_name = resolve(request.path_info).url_name
        namespace = resolve(request.path_info).namespace

        # Always skip Admin panel
        if (
            namespace == "admin"
            or namespace == "__debug__"
            or url_name in drf_logger_settings.SKIP_URL_NAME
            or namespace in drf_logger_settings.SKIP_NAMESPACE
        ):
            return

        # Only log required status codes if matching
        if (
            drf_logger_settings.STATUS_CODES is not None
            and response.status_code not in drf_logger_settings.STATUS_CODES
        ):
            return

        # Log only registered methods if available.
        if drf_logger_settings.METHODS is not None and request.method not in drf_logger_settings.METHODS:
            return

        # endregion
        data = self.get_request_log_data(request, response, start_time, end_time)  # 解析数据

        if drf_logger_settings.SIGNAL:  # 需要发送信号
            # TODO 使用django信号发送日志
            pass

        if drf_logger_settings.DATABASE:  # 需要写入数据库
            return data  # 返回数据

    def put_log_data(
        self,
        request: Request,
        response: Response,
        start_time: float,
        end_time: float | None = None,
    ) -> None:
        """
        将日志数据放入队列
        :param request:
        :param response:
        :param start_time:
        :param end_time:
        :return:
        """
        self._queue.put((request, response, start_time, end_time))

        if self._queue.qsize() >= drf_logger_settings.QUEUE_MAX_SIZE:
            # 队列已满，开始处理日志
            self._start_log_parse()

    def start_queue_process(self):
        """
        持续处理日志
        :return:
        """
        while self.flag:
            time.sleep(drf_logger_settings.INTERVAL)  # 睡眠
            if self.flag:
                self._start_log_parse()

    def _start_log_parse(self) -> None:
        """
        开始处理日志
        :return:
        """
        request_items: List[RequestLog] = []  # 请求日志
        exception_items: List[ExceptionLog] = []  # 异常日志
        while not self._queue.empty():
            try:
                request: Request
                response: Response | ApiExceptionResponse
                start_time: float
                end_time: float | None

                request, response, start_time, end_time = self._queue.get()

                # 存在异常信息，则为异常日志
                if getattr(response, "exception_data", False):
                    res = self.prepare_exception_log(request, response, start_time, end_time)
                    if res:  # 解析后需要插入数据库
                        exception_items.append(ExceptionLog(**res))
                else:  # 否则只记录请求日志
                    res = self.prepare_request_log(request, response, start_time, end_time)
                    if res:  # 解析后需要插入数据库
                        request_items.append(RequestLog(**res))
            except Exception:
                pass

        if request_items or exception_items:  # 有日志需要写入数据库
            self._insert_into_database(request_items, exception_items)

    @staticmethod
    @close_old_database_connections
    def _insert_into_database(
        request_items: List[RequestLog],
        exception_items: List[ExceptionLog],
    ) -> None:
        """
        写入数据库
        :param request_items: 请求日志列表
        :param exception_items: 异常日志列表
        :return:
        """
        try:
            if request_items:  # 有请求日志
                paperpilot_common.logs.models.RequestLog.objects.using(
                    drf_logger_settings.DEFAULT_DATABASE
                ).bulk_create(
                    request_items
                )  # 批量插入
                logger.debug(f"insert {len(request_items)} request log into database")
            if exception_items:  # 有异常日志
                # TODO 无法直接使用bulk_create: Can't bulk create a multi-table inherited model
                for item in exception_items:  # 逐条插入
                    item.save(using=drf_logger_settings.DEFAULT_DATABASE)
                logger.debug(f"insert {len(exception_items)} exception log into database")
        except OperationalError:  # 没有相关数据库表
            raise Exception(
                """
            DRF API LOGGER EXCEPTION
            Model does not exists.
            Did you forget to migrate?
            """
            )
        except Exception as e:  # 其他异常
            logger.error(f"DRF API LOGGER EXCEPTION: {e}")

    @classmethod
    def prepare_exception_log(
        cls,
        request: Request,
        response: ApiExceptionResponse,
        start_time: float,
        end_time: float | None,
    ) -> ExceptionLogDict:
        """
        解析异常记录
        :param request: 请求
        :param response: 响应
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 异常数据
        """
        data: RequestLogDict = cls.get_request_log_data(request, response, start_time, end_time)  # 获取请求日志数据
        exception_data: ApiException = response.exception_data
        data.update(
            dict(
                exp_id=exception_data.eid or "",
                event_id=exception_data.event_id or "",
                exception_type=exception_data.exc_data["type"],
                exception_msg=exception_data.exc_data["msg"],
                exception_info=exception_data.exc_data["info"],
                stack_info=exception_data.exc_data["stack"],
            )
        )
        return data

    @staticmethod
    def get_request_log_data(
        request: Request,
        response: ApiExceptionResponse,
        start_time: float,
        end_time: float | None,
    ) -> RequestLogDict:
        """
        解析请求记录
        :param request: 请求
        :param response: 响应
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return:
        """
        # region 获取用户
        jwt = request.headers.get("authorization")
        try:
            if jwt:  # 有jwt，解析
                payload = jwt.split(" ")[1].split(".")[1]
                payload = json.loads(base64.b64decode(payload + "=" * (-len(payload) % 4)).decode())
                user_id = payload.get(api_settings.USER_ID_CLAIM, None)
            else:  # 无jwt，使用request内的用户
                user_id = request.user.id if request.user.is_authenticated else None
        except Exception:
            user_id = None
        # endregion

        # region 记录请求参数
        request_param = request.GET.dict()

        request_data: Dict[str, JSONVal] = {}
        file_data: Dict[str, FileDataDict] = {}
        try:
            for key, value in response.api_request_data.items():
                if isinstance(value, UploadedFile):  # 文件
                    file_data[key]: FileDataDict = {
                        "name": value.name,
                        "size": value.size,
                        "content_type": value.content_type,
                        "content_type_extra": value.content_type_extra,
                    }
                else:  # 文本数据
                    request_data[key] = value
        except Exception:
            pass
        # endregion

        # region 记录响应数据
        response_body = {}
        try:
            if response.get("content-type") in [
                "application/json",
                "application/vnd.api+json",
            ]:  # 只记录json格式的响应
                if getattr(response, "streaming", False):  # 流式响应
                    response_body = {"__content__": "streaming"}
                else:  # 文本响应
                    if type(response.content) == bytes:  # bytes类型
                        response_body = json.loads(response.content.decode())
                    else:  # str类型
                        response_body = json.loads(response.content)
            elif "gzip" in response.get("content-type"):
                response_body = {"__content__": "gzip file"}
        except Exception:
            response_body = {"__content__": "parse error"}
        # endregion

        # region 记录url
        if drf_logger_settings.PATH_TYPE == "ABSOLUTE":
            url = request.build_absolute_uri()
        elif drf_logger_settings.PATH_TYPE == "FULL_PATH":
            url = request.get_full_path()
        else:
            url = request.build_absolute_uri()
        # endregion

        headers = get_headers(request=request)
        method = request.method

        return dict(
            user=user_id,
            ip=get_client_ip(request),
            method=method,
            url=url,
            headers=mask_sensitive_data(headers),
            content_type=request.content_type,
            query_param=mask_sensitive_data(request_param),
            request_body=mask_sensitive_data(request_data),
            file_data=file_data,
            response=mask_sensitive_data(response_body),
            status_code=response.status_code,
            execution_time=end_time - start_time if start_time and end_time else None,
            create_time=timezone.now(),
        )
