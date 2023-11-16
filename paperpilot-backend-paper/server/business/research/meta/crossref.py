from crossref.restful import Works

from server.business.research.meta.base import PaperMeta, PaperMetaFetch


class CrossRefMetaFetch(PaperMetaFetch):
    async def fetch(self, doi: str) -> PaperMeta:
        works = Works()
        work = works.doi(doi)

        title = None

        if "title" in work and len(work["title"]) > 0:
            title = work["title"][0]

        authors = None
        if "author" in work:
            authors = [
                author["given"] + " " + author["family"]
                for author in work["author"]
            ]

        publication = None
        if "container-title" in work and len(work["container-title"]) > 0:
            publication = work["container-title"][0]

        publication_year = None
        if (
            "published-print" in work
            and "date-parts" in work["published-print"]
            and len(work["published-print"]["date-parts"]) > 0
            and len(work["published-print"]["date-parts"][0]) > 0
        ):
            publication_year = work["published-print"]["date-parts"][0][0]

        url = None
        if "URL" in work:
            url = work["URL"]

        event = None
        if "event" in work and "name" in work["event"]:
            event = work["event"]["name"]

        return PaperMeta(
            title=title,
            authors=authors,
            publication=publication,
            publication_year=publication_year,
            url=url,
            event=event,
        )
