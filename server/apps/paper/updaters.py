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
        "publication_year",
        "publication",
        "event",
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


class PaperUpdater(PaperPublicUpdater):
    fields = PaperPublicUpdater.fields + ["project_id", "file"]
    logger_name = "service.paper.updater"

    async def update_file(self, obj: Paper, vo: PaperDetail) -> None:
        obj.file = vo.file

    async def update_project_id(self, obj: Paper, vo: PaperDetail) -> None:
        obj.project_id = UUID(vo.project_id)
