from crossref.restful import Works

from server.business.research.meta.base import PaperMeta, PaperMetaFetch


class CrossRefMetaFetch(PaperMetaFetch):
    async def fetch(self, doi: str) -> PaperMeta:
        works = Works()
        work = works.doi(doi)

        return PaperMeta(
            title=work["title"][0],
            authors=[
                author["given"] + " " + author["family"]
                for author in work["author"]
            ],
            publication=work["container-title"][0],
            publication_year=work["published-print"]["date-parts"][0][0],
            url=work["URL"],
        )
