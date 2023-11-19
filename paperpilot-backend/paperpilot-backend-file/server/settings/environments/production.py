from server.settings.components import config

# debug 模式
DEBUG = config("DJANGO_DEBUG", False, cast=bool)

SERVER_URL = config("SERVER_URL", "https://api.teamup.ziqiang.net.cn")
