# Logging
# https://docs.djangoproject.com/en/3.2/topics/logging/
import sys

from loguru import logger

from server.settings.components.configs import LogConfig
from server.settings.util import config

# from paperpilot_common.utils.log import configure_logging

# See also:
# 'Do not log' by Nikita Sobolev (@sobolevn)
# https://sobolevn.me/2020/03/do-not-log


LOG_LEVEL = config("LOG_LEVEL", "INFO")


# 適配loguru
LOGGING = LogConfig.get_config()

LOG_FORMAT = (
    "<green>{time:HH:mm:ss}</green> <red>|</red> "
    "<level>{level.icon}</level> <red>|</red> "
    # "<cyan>{name}</cyan>:<cyan>{function}</cyan> <red>|</red> "
    "<cyan>[{extra[title]}]</cyan> <red>-</red> <level>{message}</level>"
)

logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "level": LOG_LEVEL,
            "format": LOG_FORMAT,
        }
    ],
)

# configure_logging(LOG_FORMAT, LOG_LEVEL)
