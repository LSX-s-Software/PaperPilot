from django.core.paginator import Page, Paginator

from paperpilot_common.utils.meili.response import SearchResult
from paperpilot_common.utils.pagination import GlobalPageNumberPagination


class MeiliPaginator(Paginator):
    def __init__(
        self,
        search_result: SearchResult,
        per_page: int,
        orphans: int = 0,
        allow_empty_first_page: bool = True,
    ):
        assert search_result.hits_per_page == per_page

        super().__init__(search_result.object_list, per_page, orphans, allow_empty_first_page)

        self.result = search_result

    def _check_object_list_is_ordered(self):
        pass

    @property
    def count(self):
        return self.result.count

    @property
    def num_pages(self):
        return self.result.total_pages

    def page(self, number):
        return Page(self.object_list, int(number), self)


class MeiliPageNumberPagination(GlobalPageNumberPagination):
    django_paginator_class = MeiliPaginator
