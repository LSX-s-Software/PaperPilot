from django.db import models


class ErrorType(models.TextChoices):
    """
    错误类型
    """

    INVALID_REQUEST = "invalid_request", "无效请求"
    INTERNAL = "internal", "内部错误"
    AUTH = "auth", "认证错误"
