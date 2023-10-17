class SearchItem:
    _content: dict

    def __init__(self, content: dict):
        self._content = content

    def __getattr__(self, name):
        return self._content.get(name)

    def __getitem__(self, name):
        return self._content.get(name)


class SearchResult:
    object_list: list[SearchItem]
    page: int
    hits_per_page: int
    total_pages: int
    count: int
    facets: dict[str, dict[str, int]]
    processing_time_ms: int
    query: str

    def __init__(self, response: dict):
        self.object_list = [SearchItem(item) for item in response.get("hits")]
        self.page = response.get("page")
        self.hits_per_page = response.get("hitsPerPage")
        self.total_pages = response.get("totalPages")
        self.count = response.get("totalHits")
        self.facets = response.get("facetsDistribution", None)
        self.processing_time_ms = response.get("processingTimeMs")
        self.query = response.get("query")

    def __len__(self):
        return len(self.object_list)

    def __getitem__(self, index):
        return self.object_list[index]

    def __iter__(self):
        return iter(self.object_list)

    def __repr__(self):
        return f"<SearchResult object: {self.count} results>"
