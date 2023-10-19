import abc

from paperpilot_common.utils.log import get_logger


class PdfFile:
    url: str
    success: bool
    file: bytes

    metadata: dict

    def __init__(self, url: str, success: bool = False, file: bytes = b""):
        self.url = url
        self.success = success
        self.file = file

        self.metadata = dict()


class PdfFetch:
    logger_name = "business.research.pdf.base"

    def __init__(self):
        self.logger = get_logger(self.logger_name)

    @abc.abstractmethod
    async def fetch(self, url: str) -> PdfFile:
        """
        获取PDF文件

        :param url: PDF文件URL
        :return: PDF文件
        """
        raise NotImplementedError
