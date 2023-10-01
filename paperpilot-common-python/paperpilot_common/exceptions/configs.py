from typing import List, TypedDict

from django.conf import settings
from django.core.signals import setting_changed
from django.dispatch import receiver

from paperpilot_common.utils.package_settings import PackageSettings

ZqExceptionSettingDict = TypedDict(
    "ZqExceptionSettingDict",
    {
        "EXCEPTION_UNKNOWN_HANDLE": bool,
        "EXCEPTION_HANDLER_CLASS": str,
    },
    total=True,
)


class ZqExceptionSettings(PackageSettings):
    setting_name = "ZQ_EXCEPTION"

    DEFAULTS: ZqExceptionSettingDict = {
        "EXCEPTION_UNKNOWN_HANDLE": True,  # 处理未知异常
        "EXCEPTION_HANDLER_CLASS": "paperpilot_common.exceptions.handler.ApiExceptionHandler",
    }

    IMPORT_STRINGS: List[str] = ["EXCEPTION_HANDLER_CLASS"]

    SENTRY_ENABLE: bool = getattr(settings, "SENTRY_ENABLE", False)


zq_exception_settings = ZqExceptionSettings()


@receiver(setting_changed)
def reload_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "SENTRY_ENABLE":
        zq_exception_settings.SENTRY_ENABLE = getattr(settings, "SENTRY_ENABLE", False)
    zq_exception_settings.reload_package_settings(*args, **kwargs)
