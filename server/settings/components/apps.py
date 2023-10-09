DJANGO_APPS: list[str] = [
    "simpleui",  # admin ui
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS: list[str] = [
    "paperpilot_common.oss",  # oss
    "django_extensions",  # Django 扩展
    # "cacheops",  # ORM缓存
    "paperpilot_common.grpc",  # grpc
    "paperpilot_common.utils.admin_logs",  # admin日志
]

LOCAL_APPS: list[str] = [
    "user",  # 用户
    "oauth",  # 认证
]

INSTALLED_APPS: list[str] = (
    DJANGO_APPS
    + THIRD_PARTY_APPS
    + LOCAL_APPS
    + ["django_cleanup.apps.CleanupConfig"]  # 清理OSS文件, 需要放在最后
)

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "server.urls"

WSGI_APPLICATION = "server.wsgi.application"
ASGI_APPLICATION = "server.asgi.application"
