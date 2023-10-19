import datetime
from uuid import UUID

from paper.models import Paper
from paperpilot_common.protobuf.paper.paper_pb2 import PaperDetail
from paperpilot_common.utils.updater import Updater


class PaperPublicUpdater(Updater):
    fields = [
        "title",
        "abstract",
        "keywords",
        "authors",
        "tags",
        "publication_date",
        "publication",
        "volume",
        "issue",
        "pages",
        "doi",
        "url",
    ]
    logger_name = "service.paper.public_updater"

    async def update_keywords(self, obj: Paper, vo: PaperDetail) -> None:
        obj.keywords = list(vo.keywords)

    async def update_authors(self, obj: Paper, vo: PaperDetail) -> None:
        obj.authors = list(vo.authors)

    async def update_tags(self, obj: Paper, vo: PaperDetail) -> None:
        obj.tags = list(vo.tags)

    async def diff_publication_date(self, obj: Paper, vo: PaperDetail) -> bool:
        if (
            obj.publication_date is not None
            and vo.publication_date.ByteSize() > 0
        ):  # 均存在有效值
            return (
                obj.publication_date.year != vo.publication_date.year
                or obj.publication_date.month != vo.publication_date.month
                or obj.publication_date.day != vo.publication_date.day
            )

        if (
            obj.publication_date and vo.publication_date.ByteSize() == 0
        ):  # 均不存在有效值
            return False

        return True

    async def update_publication_date(
        self, obj: Paper, vo: PaperDetail
    ) -> None:
        if vo.publication_date.ByteSize() == 0:
            obj.publication_date = None
        else:
            obj.publication_date = datetime.date(
                year=vo.publication_date.year,
                month=vo.publication_date.month,
                day=vo.publication_date.day,
            )


class PaperUpdater(PaperPublicUpdater):
    fields = PaperPublicUpdater.fields + ["project_id", "file"]
    logger_name = "service.paper.updater"

    async def update_file(self, obj: Paper, vo: PaperDetail) -> None:
        obj.file = vo.file

    async def update_project_id(self, obj: Paper, vo: PaperDetail) -> None:
        obj.project_id = UUID(vo.project_id)
