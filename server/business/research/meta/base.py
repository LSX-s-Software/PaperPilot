import abc

from paperpilot_common.utils.log import get_logger


class PaperMeta:
    title: str | None
    authors: list[str] | None
    publication: str | None
    publication_year: int | None
    url: str | None
    event: str | None

    def __init__(
        self,
        title: str | None = None,
        authors: list[str] | None = None,
        publication: str | None = None,
        publication_year: int | None = None,
        url: str | None = None,
        event: str | None = None,
    ):
        self.title = title
        self.authors = authors
        self.publication = publication
        self.publication_year = publication_year
        self.url = url
        self.event = event


class PaperMetaFetch:
    logger_name = "business.research.meta.base"

    def __init__(self):
        self.logger = get_logger(self.logger_name)

    @abc.abstractmethod
    async def fetch(self, doi: str) -> PaperMeta:
        """
        获取论文元数据

        :param doi: 论文 doi
        :return: 元数据
        """
        raise NotImplementedError
