import base64
import datetime
import hashlib
import hmac
import json
import random
import time
from typing import AnyStr, Dict, Optional, Tuple, TypedDict
from urllib.parse import unquote
from urllib.request import urlopen

from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from django.core.cache import cache
from rest_framework.request import Request

from paperpilot_common.utils.oss.configs import oss_settings
from paperpilot_common.utils.types import JSONValue


class OSSCallbackToken(TypedDict):
    OSSAccessKeyId: str
    host: str
    policy: str
    signature: str
    expire: str
    key: str
    callback: str


def get_iso_8601(expire: float) -> str:
    gmt = datetime.datetime.utcfromtimestamp(expire).isoformat()
    gmt += "Z"
    return gmt


def split_file_name(file_name: str) -> Tuple[str, str]:
    """
    获取文件名与扩展名

    :param file_name: 文件全名

    :return: 文件名，扩展名
    """
    if "." in file_name:  # 文件存在扩展名
        ext = file_name.split(".")[-1]  # 文件扩展名
        name = ".".join(file_name.split(".")[0:-1])
    else:
        ext = ""
        name = file_name

    return name, ext


def get_random_name(file_name: str) -> str:
    """
    获取随机文件名

    :param file_name: 原文件名

    :return:
    """
    name, ext = split_file_name(file_name)

    new_name = time.strftime("%Y%m%d%H%M%S")  # 定义文件名，年月日时分秒随机数
    new_name = new_name + "_%04d" % random.randint(0, 10000) + (("." + ext) if ext != "" else "")

    return new_name


def get_token(
    key: str,
    callback: Dict[str, str],
    policy: Optional[JSONValue] = None,
) -> OSSCallbackToken:
    """
    获取直传签名token
    """
    # 获取Policy
    expire_time = datetime.datetime.now() + datetime.timedelta(seconds=oss_settings.TOKEN_EXPIRE_SECOND)
    expire = get_iso_8601(expire_time.timestamp())
    if policy is None:
        policy = {
            "expiration": expire,  # 过期时间
            "conditions": [
                {"bucket": oss_settings.BUCKET_NAME},
                [
                    "content-length-range",
                    0,
                    oss_settings.MAX_SIZE_MB * 1024 * 1024,
                ],  # 限制上传文件大小
                ["eq", "$key", f"{key}"],  # 限制上传文件名
            ],
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

    # 回调参数
    callback_param = json.dumps(callback).strip()
    base64_callback_body = base64.b64encode(callback_param.encode())

    return dict(
        OSSAccessKeyId=oss_settings.ACCESS_KEY_ID,
        host=(
            f'{oss_settings.ENDPOINT.split("://")[0]}://{oss_settings.BUCKET_NAME}.'
            f'{oss_settings.ENDPOINT.split("://")[1]}'
        ),
        policy=policy_encode.decode(),
        signature=sign.decode(),
        expire=expire,
        key=key,
        callback=base64_callback_body.decode(),
    )


def check_callback_signature(request: Request) -> bool:
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


def _get_pub_key_online(pub_key_url: str) -> AnyStr:
    """
    从网络获取pub key
    """
    response = urlopen(pub_key_url)
    return response.read()


def get_pub_key(pub_key_url: str) -> AnyStr:
    """
    获取公钥
    :param pub_key_url: url
    :return:
    """
    key = f"oss:pub_key:{pub_key_url}"

    try:
        res = cache.get(key, None)
        if res is None:
            res = _get_pub_key_online(pub_key_url)
            cache.set(key, res)
        return res
    except Exception:
        return _get_pub_key_online(pub_key_url)
