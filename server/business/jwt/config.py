import datetime

from django.conf import settings

config = settings.JWT


access_lifetime: datetime.timedelta = config.get(
    "ACCESS_TOKEN_LIFETIME", datetime.timedelta(days=1)
)
refresh_lifetime: datetime.timedelta = config.get(
    "REFRESH_TOKEN_LIFETIME", datetime.timedelta(days=30)
)

algorithm = config.get("ALGORITHM", "HS256")

secret = settings.SECRET_KEY
