import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import unquote

from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from django.conf import settings

from .configs import oss_settings
from .utils import Condition, OssDirectToken, get_iso_8601, get_pub_key, handle_condition, parse_size

default_callback_body = (
    "object=${object}&"
    "size=${size}&"
    "mime_type=${mimeType}&"
    "height=${imageInfo.height}&"
    "width=${imageInfo.width}&"
    "etag=${etag}&"
    "client_ip=${clientIp}&"
)


def generate_direct_upload_token(
    callback_url: str,
    callback_body: str = default_callback_body,
    min_size: int | str = 0,
    max_size: int | str = oss_settings.MAX_SIZE_MB,
    key: str | list[str] | Condition = None,
    cache_control: str | list[str] | Condition = None,
    content_type: str | list[str] | Condition = None,
    content_disposition: str | list[str] | Condition = None,
    content_encoding: str | list[str] | Condition = None,
    expires: str | list[str] | Condition = None,
    success_action_redirect: str | list[str] | Condition = None,
    success_action_status: str | list[str] | Condition = None,
    x_oss_meta: dict[str, str | list[str] | Condition] = None,
) -> OssDirectToken:
    """
    获取直传 Token

    :param callback_url: 回调地址（不含host）
    :param callback_body: 回调内容，形如key=${object}&etag=${etag}&my_var=${x:my_var}
    :param min_size: 最小文件大小
    :param max_size: 最大文件大小
    :param key: 文件存储路径（含文件名，不包括MEDIA_URL）
    :param cache_control: 缓存控制（HTTP请求Header）
    :param content_type: 类型（HTTP请求Header）
    :param content_disposition: 附件（HTTP请求Header）
    :param content_encoding: 编码（HTTP请求Header）
    :param expires: 缓存过期时间（HTTP请求Header）
    :param success_action_redirect: 上传成功后跳转地址
    :param success_action_status: 未指定success_action_redirect时，上传成功后的返回状态码
    :param x_oss_meta: 自定义元数据，限定表单域的行为
    :return: 直传 Token
    """
    # 统一callback_url格式
    if callback_url.startswith("/"):
        callback_url = callback_url[1:]
    if oss_settings.CALLBACK_BASE_URL.endswith("/"):
        callback_base_url = oss_settings.CALLBACK_BASE_URL[:-1]
    else:
        callback_base_url = oss_settings.CALLBACK_BASE_URL
    callback_complete_url = f"{callback_base_url}/{callback_url}"

    # 获取Policy，完整参数详见
    # https://help.aliyun.com/zh/oss/developer-reference/postobject?spm=a2c4g.11186623.0.i26#section-d5z-1ww-wdb

    # 处理限制
    conditions = [
        {"bucket": oss_settings.BUCKET_NAME},
        ["content-length-range", parse_size(min_size), parse_size(max_size)],  # 限制上传文件大小
    ]

    handle_condition(conditions, "key", f"{settings.MEDIA_URL}{key}")
    handle_condition(conditions, "cache-control", cache_control)
    handle_condition(conditions, "content-type", content_type)
    handle_condition(conditions, "content-disposition", content_disposition)
    handle_condition(conditions, "content-encoding", content_encoding)
    handle_condition(conditions, "expires", expires)
    handle_condition(conditions, "success_action_redirect", success_action_redirect)
    handle_condition(conditions, "success_action_status", success_action_status)

    if x_oss_meta:
        for k, v in x_oss_meta.items():
            handle_condition(conditions, f"x-oss-meta-{k}", v)

    expire_time = datetime.datetime.now() + datetime.timedelta(seconds=oss_settings.TOKEN_EXPIRE_SECOND)
    expire = get_iso_8601(expire_time.timestamp())
    policy = {
        "expiration": expire,  # 过期时间
        "conditions": conditions,
    }
    policy = json.dumps(policy).strip()
    policy_encode = base64.b64encode(policy.encode())

    # 签名
    h = hmac.new(
        oss_settings.ACCESS_KEY_SECRET.encode(),
        policy_encode,
        hashlib.sha1,
    )
    sign = base64.encodebytes(h.digest()).strip()

    # 回调参数，详见
    # https://help.aliyun.com/zh/oss/developer-reference/callback?spm=a2c4g.11186623.0.i74#a8a8e930e31fv
    callback_dict = {
        "callbackUrl": callback_complete_url,
        "callbackBody": callback_body,
        "callbackBodyType": "application/x-www-form-urlencoded",
    }

    callback_param = json.dumps(callback_dict).strip()
    base64_callback_body = base64.b64encode(callback_param.encode())

    host = (
        f'{oss_settings.ENDPOINT.split("://")[0]}://{oss_settings.BUCKET_NAME}.'
        f'{oss_settings.ENDPOINT.split("://")[1]}'
    )

    return OssDirectToken(
        access_key_id=oss_settings.ACCESS_KEY_ID,
        host=host,
        policy=policy_encode.decode(),
        signature=sign.decode(),
        callback=base64_callback_body.decode(),
    )


def check_callback_signature(request) -> bool:
    """
    检测回调身份
    """
    authorization_base64 = request.META.get("HTTP_AUTHORIZATION", None)  # 获取AUTHORIZATION
    pub_key_url_base64 = request.META.get("HTTP_X_OSS_PUB_KEY_URL", None)  # 获取公钥
    if authorization_base64 is None or pub_key_url_base64 is None:
        return False

    try:
        # 对x-oss-pub-key-url做base64解码后获取到公钥
        pub_key_url = base64.b64decode(pub_key_url_base64).decode()

        # 为了保证该public_key是由OSS颁发的，用户需要校验x-oss-pub-key-url的开头
        if not pub_key_url.startswith("http://gosspublic.alicdn.com/") and not pub_key_url.startswith(
            "https://gosspublic.alicdn.com/"
        ):
            return False
        pub_key = get_pub_key(pub_key_url)

        # 获取base64解码后的签名
        authorization = base64.b64decode(authorization_base64)

        # 获取待签名字符串
        callback_body = request.body

        if request.META["QUERY_STRING"] == "":
            auth_str = unquote(request.META["PATH_INFO"]) + "\n" + callback_body.decode()
        else:
            auth_str = (
                unquote(request.META["PATH_INFO"]) + "?" + request.META["QUERY_STRING"] + "\n" + callback_body.decode()
            )

        # 验证签名
        auth_md5 = MD5.new(auth_str.encode())
        rsa_pub = RSA.importKey(pub_key)
        verifier = PKCS1_v1_5.new(rsa_pub)
        verifier.verify(auth_md5, authorization)
        return True
    except Exception:
        return False
