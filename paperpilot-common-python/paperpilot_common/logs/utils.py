import re
from typing import Dict

from django.db import close_old_connections
from rest_framework.request import Request

from paperpilot_common.logs.configs import drf_logger_settings
from paperpilot_common.response.types import JSONVal


def get_headers(request: Request = None) -> Dict[str, str]:
    """
    Function:       get_headers(self, request)
    Description:    To get all the headers from request
    """
    regex = re.compile("^HTTP_")
    return dict(
        (regex.sub("", header), value) for (header, value) in request.META.items() if header.startswith("HTTP_")
    )


def get_client_ip(request: Request) -> str:
    try:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
    except Exception:
        return ""


def is_api_logger_enabled() -> bool:
    return drf_logger_settings.DATABASE or drf_logger_settings.SIGNAL


def database_log_enabled() -> bool:
    return drf_logger_settings.DATABASE


def mask_sensitive_data(data: JSONVal) -> JSONVal:
    """
    Hides sensitive keys specified in sensitive_keys settings.
    Loops recursively over nested dictionaries.
    """

    if type(data) != dict:
        return data

    for key, value in data.items():
        if key in drf_logger_settings.SENSITIVE_KEYS:
            length = len(data[key])
            data[key] = f"***FILTERED*** (len: {length})"

        if type(value) == dict:
            data[key] = mask_sensitive_data(data[key])

        if type(value) == list:
            data[key] = [mask_sensitive_data(item) for item in data[key]]

    return data


def close_old_database_connections(func):
    """
    自定义decorator，用来装饰使用数据库操作函数

    https://stackoverflow.com/questions/59773675/why-am-i-getting-the-mysql-server-has-gone-away-exception-in-django
    """

    def wrapper(*args, **kwargs):
        close_old_connections()

        return func(*args, **kwargs)

    return wrapper
