import aiohttp
import random
from hashlib import md5

from server.business.baidu.config import APPID, APPKEY


class Translation:
    appid = APPID
    appkey = APPKEY
    endpoint = "https://api.fanyi.baidu.com"
    path = "/api/trans/vip/translate"
    url = endpoint + path

    salt = random.randint(32768, 65536)

    @staticmethod
    def make_md5(s, encoding="utf-8"):
        return md5(s.encode(encoding)).hexdigest()

    async def translate(
        self, query: str, from_lang: str = "auto", to_lang: str = "zh"
    ) -> str:
        """
        翻译文字

        :param query: 待翻译文字
        :param from_lang: 源语言
        :param to_lang: 目标语言
        :return: 翻译结果
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                params={
                    "appid": self.appid,
                    "q": query,
                    "from": from_lang,
                    "to": to_lang,
                    "salt": self.salt,
                    "sign": self.make_md5(
                        self.appid + query + str(self.salt) + self.appkey
                    ),
                },
            ) as resp:
                result = await resp.json()

        return result["trans_result"][0]["dst"]
