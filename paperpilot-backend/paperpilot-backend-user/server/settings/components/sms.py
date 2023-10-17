# region 阿里云SMS
from server.settings.util import config

SMS_ENABLE = config("SMS_ENABLE", cast=bool, default=False)
ALIYUN_SMS_ACCESS_KEY_ID = config("ALIYUN_SMS_ACCESS_KEY_ID", None)
ALIYUN_SMS_ACCESS_KEY_SECRET = config("ALIYUN_SMS_ACCESS_KEY_SECRET", None)
ALIYUN_SMS_SIGN_NAME = config("ALIYUN_SMS_SIGN_NAME", None)
ALIYUN_SMS_TEMPLATE_CODE = config("ALIYUN_SMS_TEMPLATE_CODE", None)
# endregion
