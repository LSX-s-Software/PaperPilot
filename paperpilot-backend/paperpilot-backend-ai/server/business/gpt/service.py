import json

import aiohttp
from paperpilot_common.utils.log import get_logger

from server.business.gpt.config import proxy, url


class GptBusiness:
    logger = get_logger("business.gpt")
    url = url
    proxy = proxy
    session: aiohttp.ClientSession | None = None

    def __init__(self):
        self.headers = {
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        }

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    @staticmethod
    def generate_payload(content: list[dict[str, str]]) -> str:
        return json.dumps(
            {
                "messages": content,
                "model": "gpt-3.5-turbo",
                "temperature": 1,
                "presence_penalty": 0,
                "top_p": 1,
                "frequency_penalty": 0,
                "stream": True,
            },
            ensure_ascii=False,
        )

    async def ask(self, content: list[dict[str, str]]) -> (str, str | None):
        """
        ask question to gpt

        :param content: question
        :return: (answer, finish_reason)
        """
        await self.init_session()
        self.logger.debug(f"Ask: {content}")
        payload = self.generate_payload(content)
        async with self.session.post(
            url, data=payload, headers=self.headers, proxy=self.proxy
        ) as r:
            async for line in r.content:
                if line == b"\n":
                    continue
                if line == b"data: [DONE]\n":
                    continue

                data = json.loads(line[6:])
                if not data["choices"][0]["finish_reason"]:
                    yield data["choices"][0]["delta"]["content"], None
                else:
                    yield "", data["choices"][0]["finish_reason"]

    async def close(self):
        if self.session:
            await self.session.close()
