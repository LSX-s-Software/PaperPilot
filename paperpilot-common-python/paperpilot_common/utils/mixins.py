from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.viewsets import GenericViewSet

CACHE_TTL = getattr(settings, "CACHE_TTL", 60 * 60 * 1)


class CacheListModelMixin:
    @method_decorator(cache_page(CACHE_TTL))
    def list(self: "GenericViewSet", request: "Request", *args: Any, **kwargs: Any) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CacheRetrieveModelMixin:
    @method_decorator(cache_page(CACHE_TTL))
    def retrieve(self: "GenericViewSet", request: "Request", *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
