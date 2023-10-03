from django.conf import settings

access_key_id = settings.ALIYUN_SMS_ACCESS_KEY_ID
access_key_secret = settings.ALIYUN_SMS_ACCESS_KEY_SECRET

enable = settings.SMS_ENABLE
sign_name = settings.ALIYUN_SMS_SIGN_NAME
template = {
    "code": settings.ALIYUN_SMS_TEMPLATE_CODE,
}
