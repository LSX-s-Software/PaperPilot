from aiohttp import ClientSession
from bs4 import BeautifulSoup

from server.business.research.pdf.base import PdfFetch, PdfFile
from server.business.research.pdf.config import SCIHUB_BASE_URL


class ScihubFetch(PdfFetch):
    base_url = SCIHUB_BASE_URL
    logger_name = "business.research.pdf.scihub"

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "max-age=0",
        "cookie": "__ddg1_=1GAoUhrB0RU860jnf1TF; __ddgid_=qPbabu1pPpfcBHqx; __ddg2_=k7EVSml33KNBOnxk; "
        "session=03fdc3941df3716a4858006e406715f0; language=cn; refresh=1697612891.6165",
        "sec-ch-ua": '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46",
        "x-forwarded-for": "4.2.2.2",
    }

    def __init__(self):
        super().__init__()
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]
        self.headers["authority"] = self.base_url.split("//")[1].split("/")[0]
        self.session = None

    async def _create_session(self):
        if self.session is None:
            self.session = ClientSession(headers=self.headers)

    async def _download(self, url: str) -> bytes:
        async with self.session.get(url) as response:
            self.logger.debug(f"download {url}, status: {response.status}")
            if response.status != 200:
                raise Exception(
                    f"download {url} failed, status: {response.status}"
                )
            return await response.read()

    async def parse(self, pdf_file: PdfFile, html: str) -> PdfFile:
        soup = BeautifulSoup(html, "html.parser")
        pdf_url = soup.find("embed", {"id": "pdf"}).attrs["src"]
        self.logger.debug(f"pdf_url: {pdf_url}")
        pdf_file.file = await self._download(f"{self.base_url}/{pdf_url}")
        pdf_file.success = True

        try:
            metadata = soup.find("div", {"id": "citation"}).text.split(". ")

            if len(metadata) == 5:
                pdf_file.metadata = {
                    "author": [
                        f"{author.strip().strip('&').strip()}."
                        for author in metadata[0].split("., ")
                    ],
                    "year": int(metadata[1][1:-1]),
                    "title": metadata[2],
                    "publication": metadata[3],
                    "doi": metadata[4].strip("doi:").strip(),
                }
        except Exception as e:
            self.logger.debug(f"parse metadata failed: {e}")

        return pdf_file

    async def fetch(self, url: str) -> PdfFile:
        """
        获取PDF文件

        :param url: PDF文件URL
        :return: PDF文件
        """
        await self._create_session()

        async with self.session.get(f"{self.base_url}/{url}") as response:
            text = await response.text()

        file = PdfFile(url)

        try:
            file = await self.parse(file, text)
        except Exception as e:
            self.logger.debug(f"parse failed: {e}")

        return file


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        ScihubFetch().fetch(
            "https://ieeexplore.ieee.org/abstract/document/8952379"
        )
    )
