import base64
from typing import AnyStr
from urllib.parse import unquote

import aiohttp
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from paperpilot_common.utils.log import get_logger


class OssCallbackChecker:
    HTTP_ADDR = "http://gosspublic.alicdn.com/"
    HTTPS_ADDR = "https://gosspublic.alicdn.com/"

    logger = get_logger("oss.callback.checker")
    cache = None
    pub_key = {}
    verifier = {}

    async def _get_pub_key_online(self, pub_key_url: str) -> AnyStr:
        """
        从网络获取pub key
        """
        self.logger.debug(f"get pub key online from {pub_key_url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(pub_key_url) as response:
                if response.status == 200:
                    file_data = await response.read()
                    return file_data
                else:
                    raise Exception(f"get pub key online failed, status: {response.status}")

    async def get_pub_key(self, pub_key_url: str) -> AnyStr:
        """
        获取公钥
        :param pub_key_url: url
        :return:
        """
        key = f"oss:pub_key:{pub_key_url}"

        try:
            res = await self.cache.get(key, None)
            if res is None:
                res = self._get_pub_key_online(pub_key_url)
                await self.cache.set(key, res)
            return res
        except Exception as e:
            self.logger.warning(f"get pub key failed, url: {pub_key_url}, fallback to local cache")
            self.logger.exception(e)

            if self.pub_key.get(pub_key_url, None) is None:
                self.pub_key[pub_key_url] = await self._get_pub_key_online(pub_key_url)

            return self.pub_key[pub_key_url]

    async def get_verifier(self, pub_key_url_base64: str) -> PKCS1_v1_5:
        """
        获取验证器
        :param pub_key_url_base64: url base64
        :return:
        """
        if self.verifier.get(pub_key_url_base64, None) is None:
            # 对x-oss-pub-key-url做base64解码后获取到公钥
            pub_key_url = base64.b64decode(pub_key_url_base64).decode()

            # 为了保证该public_key是由OSS颁发的，用户需要校验x-oss-pub-key-url的开头
            if not pub_key_url.startswith(self.HTTP_ADDR) and not pub_key_url.startswith(self.HTTPS_ADDR):
                raise Exception("pub_key_url is invalid")
            pub_key = await self.get_pub_key(pub_key_url)
            rsa_pub = RSA.importKey(pub_key)
            self.verifier[pub_key_url_base64] = PKCS1_v1_5.new(rsa_pub)

        return self.verifier[pub_key_url_base64]

    async def check_callback_signature(
        self, headers: dict[str, str], query_string: str, path_info: str, body: bytes
    ) -> bool:
        """
        检测回调身份

        :param headers: 请求头
        :param query_string: 查询字符串
        :param path_info: 路径
        :param body: 请求体
        :return: 是否通过
        """
        authorization_base64 = headers.get("AUTHORIZATION", None)  # 获取AUTHORIZATION
        pub_key_url_base64 = headers.get("X-OSS-PUB-KEY-URL", None)  # 获取公钥
        if authorization_base64 is None or pub_key_url_base64 is None:
            return False

        try:
            verifier = await self.get_verifier(pub_key_url_base64)

            # 获取base64解码后的签名
            authorization = base64.b64decode(authorization_base64)

            # 获取待签名字符串
            callback_body = body

            if query_string == "":
                auth_str = unquote(path_info) + "\n" + callback_body.decode()
            else:
                auth_str = unquote(path_info) + "?" + query_string + "\n" + callback_body.decode()

            # 验证签名
            auth_md5 = MD5.new(auth_str.encode())
            return verifier.verify(auth_md5, authorization)
        except Exception:
            return False
