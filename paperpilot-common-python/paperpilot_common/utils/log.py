import sys

from loguru import logger as default_logger

_logger = default_logger.bind(title="main")

default_fmt = (
    "<green>{time:HH:mm:ss}</green> <red>|</red> "
    "<level>{level.icon}</level> <red>|</red> "
    # "<cyan>{name}</cyan>:<cyan>{function}</cyan> <red>|</red> "
    "<cyan>[{extra[title]}]</cyan> <red>-</red> <level>{message}</level>"
)


def configure_logging(fmt: str, level: str):
    _logger.remove()
    _logger.add(sys.stdout, format=fmt, level=level)


# configure_logging(settings.LOG_FORMAT, settings.LOG_LEVEL)


def get_logger(title: str | None = None):
    """
    Get logger
    :param title: title of logger (default: None)
    :return: logger
    """
    return _logger.bind(title=title) if title else _logger
