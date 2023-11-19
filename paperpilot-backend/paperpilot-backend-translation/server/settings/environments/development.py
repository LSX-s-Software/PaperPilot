"""
This file contains all the settings that defines the development server.

SECURITY WARNING: don't run with debug turned on in production!
"""

import socket

from loguru import logger

from server.settings.components.apps import INSTALLED_APPS, MIDDLEWARE
from server.settings.util import config

# Setting the development status:

DEBUG = True

SERVER_URL = config("SERVER_URL", "https://api.test.teamup.ziqiang.net.cn")

ALLOWED_HOSTS = ["*"]

# Installed apps for development only:

INSTALLED_APPS += [
    "paperpilot_common.utils.watcher",
    # Better debug:
    "debug_toolbar",
    "nplusone.ext.django",
    # Linting migrations:
    "django_migration_linter",
    # django-extra-checks:
    "extra_checks",
]


# Django debug toolbar:
# https://django-debug-toolbar.readthedocs.io

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # https://github.com/bradmontgomery/django-querycount
    # Prints how many queries were executed, useful for the APIs.
    "querycount.middleware.QueryCountMiddleware",
]

# https://django-debug-toolbar.readthedocs.io/en/stable/installation.html#configure-internal-ips
try:  # This might fail on some OS
    INTERNAL_IPS = [
        "{0}.1".format(ip[: ip.rfind(".")])
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]
    ]
except socket.error:  # pragma: no cover
    INTERNAL_IPS = []
INTERNAL_IPS += ["127.0.0.1"]


def _custom_show_toolbar(request):
    """Only show the debug toolbar when in the debug mode"""
    return DEBUG


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "server.settings.environments.development._custom_show_toolbar",
}

# django-querycount
# https://github.com/bradmontgomery/django-querycount
QUERYCOUNT = {
    "THRESHOLDS": {
        "MEDIUM": 50,
        "HIGH": 200,
        "MIN_TIME_TO_LOG": 0,
        "MIN_QUERY_COUNT_TO_LOG": 0,
    },
    "IGNORE_REQUEST_PATTERNS": [
        r"^/admin/.*",
        r"^/static/.*",
        r"^/media/.*",
        r"^/favicon.ico$",
        r"^/robots.txt$",
        r"^/api/$",
        r"^/api$",
        r"^/$",
    ],
    "IGNORE_SQL_PATTERNS": [],
    "DISPLAY_DUPLICATES": None,
    "RESPONSE_HEADER": "X-DjangoQueryCount-Count",
}


# nplusone
# https://github.com/jmcarp/nplusone

# Should be the first in line:
MIDDLEWARE = [  # noqa: WPS440
    "nplusone.ext.django.NPlusOneMiddleware",
] + MIDDLEWARE

# Logging N+1 requests:
NPLUSONE_RAISE = False  # comment out if you want to allow N+1 requests
NPLUSONE_LOGGER = logger
NPLUSONE_LOG_LEVEL = "WARNING"
NPLUSONE_WHITELIST = [
    {"model": "admin.*"},
]


# django-test-migrations
# https://github.com/wemake-services/django-test-migrations

# Set of badly named migrations to ignore:
DTM_IGNORED_MIGRATIONS = frozenset((("axes", "*"),))


# django-extra-checks
# https://github.com/kalekseev/django-extra-checks


def skip_if_symmetrical_is_not(field, *args, **kwargs):
    if field.remote_field is None:
        return False
    return not field.remote_field.symmetrical


EXTRA_CHECKS = {
    "checks": [
        # 所有模型字段需要verbose_name解释:
        "field-verbose-name",
        # Forbid `unique_together`:
        "no-unique-together",
        # Require non empty `upload_to` argument:
        "field-file-upload-to",
        # Use the indexes option instead:
        "no-index-together",
        # Each model must be registered in admin:
        "model-admin",
        # FileField/ImageField must have non-empty `upload_to` argument:
        "field-file-upload-to",
        # Text fields shouldn't use `null=True`:
        "field-text-null",
        # Don't pass `null=False` to model fields (this is django default)
        "field-null",
        # ForeignKey fields must specify db_index explicitly if used in
        # other indexes:
        {"id": "field-foreign-key-db-index", "when": "indexes"},
        # If field nullable `(null=True)`,
        # then default=None argument is redundant and should be removed:
        "field-default-null",
        #  Related fields must specify related_name explicitly:
        {"id": "field-related-name", "skipif": skip_if_symmetrical_is_not},
    ],
}

WATCHFILES = [
    "server/apps/",
    "server/settings/",
    "server/utils/",
    "server/urls.py",
    "config/",
    "manage.py",
]
