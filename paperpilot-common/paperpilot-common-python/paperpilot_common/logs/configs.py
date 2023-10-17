from typing import List, Optional, TypedDict

from django.core.signals import setting_changed
from django.dispatch import receiver

from paperpilot_common.utils.package_settings import PackageSettings

DrfLoggerSettingDict = TypedDict(
    "DrfLoggerSettingDict",
    {
        "DEFAULT_DATABASE": str,
        "QUEUE_MAX_SIZE": int,
        "INTERVAL": int,
        "DATABASE": bool,
        "SIGNAL": bool,
        "PATH_TYPE": str,
        "SKIP_URL_NAME": List[str],
        "SKIP_NAMESPACE": List[str],
        "METHODS": Optional[List[str]],
        "STATUS_CODES": Optional[List[int]],
        "SENSITIVE_KEYS": List[str],
        "ADMIN_SLOW_API_ABOVE": int,  # ms
        "ADMIN_TIMEDELTA": int,  # minute
    },
    total=True,
)


class DrfLoggerSettings(PackageSettings):
    setting_name = "DRF_LOGGER"

    DEFAULTS: DrfLoggerSettingDict = {
        "DEFAULT_DATABASE": "default",
        "QUEUE_MAX_SIZE": 50,
        "INTERVAL": 10,
        "DATABASE": False,
        "SIGNAL": False,
        "PATH_TYPE": "FULL_PATH",
        "SKIP_URL_NAME": [],
        "SKIP_NAMESPACE": [],
        "METHODS": None,
        "STATUS_CODES": None,
        "SENSITIVE_KEYS": ["password", "token", "access", "refresh"],
        "ADMIN_SLOW_API_ABOVE": 500,
        "ADMIN_TIMEDELTA": 0,
    }

    IMPORT_STRINGS: List[str] = []


drf_logger_settings = DrfLoggerSettings()


@receiver(setting_changed)
def reload_settings(*args, **kwargs):
    drf_logger_settings.reload_package_settings(*args, **kwargs)
