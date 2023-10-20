"""
This file contains all the settings that defines the development server.

SECURITY WARNING: don't run with debug turned on in production!
"""

import socket

from loguru import logger

from server.settings.util import config

# Setting the development status:

DEBUG = True

SERVER_URL = config("SERVER_URL", "https://api.test.teamup.ziqiang.net.cn")

WATCHFILES = [
    "server/apps/",
    "server/settings/",
    "server/utils/",
    "server/urls.py",
    "config/",
    "manage.py",
]
