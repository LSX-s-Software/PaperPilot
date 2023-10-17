from typing import Any, Type

import meilisearch.index
from django.db.models import Model, QuerySet
from meilisearch import Client
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer

from paperpilot_common.utils.meili.response import SearchResult

PK = int | str


class BaseIndex(meilisearch.index.Index):
    """
    Index class for MeiliSearch

    index是多个具有同类型document的集合，每个document都有一个唯一的标识符，称为主键。
    该类用于以类字段的形式定义index的设置，以及对index的增删改查操作。

    :var index_uid: index的唯一标识符 (str)
    :var primary_key: 主键 (str | None, 默认为 None, 即自动识别主键)
    :var client: MeiliSearch client (Client | None, 默认为None, 即使用 meili_client 单例)
    :var class_settings: 是否使用类属性作为index的设置 (bool, 默认为 True)

    :var displayed_attributes: 要显示的字段 (list[str], 默认为 ["*"], 即全部字段)
    :var searchable_attributes: 要搜索的字段 (list[str], 默认为 ["*"], 即全部字段)
    :var filterable_attributes: 要对值进行筛选的字段 (list[str], 默认为 [])
    :var sortable_attributes: 要排序的字段 (list[str], 默认为 [])
    :var ranking_rules: 排序规则 (list[str], 默认为 ["typo", "words", "proximity", "attribute", "sort", "exactness"])
    :var stop_words: 停用词 (list[str], 默认为 [])
    :var synonyms: 同义词 (dict[str, list[str]], 默认为 {})
    :var distinct_attribute: 去重字段 (str | None, 默认为 None)
    :var max_values_per_facet: 每个facet的最大值 (int, 默认为 100)
    :var max_total_hits: 搜索结果数目的最大值, 用于分页 (int, 默认为 1000)
    """

    index_uid: str
    primary_key: str | None = None
    client: Client | None = None

    class_settings: bool = True

    # global
    displayed_attributes: list[str] = ["*"]
    searchable_attributes: list[str] = ["*"]
    filterable_attributes: list[str] = []
    sortable_attributes: list[str] = []
    ranking_rules: list[str] = [
        "typo",
        "words",
        "proximity",
        "attribute",
        "sort",
        "exactness",
    ]
    stop_words: list[str] = []
    synonyms: dict[str, list[str]] = {}
    distinct_attribute: str | None = None

    # faceting
    max_values_per_facet: int = 100

    # pagination
    max_total_hits: int = 1000

    _instance: "BaseIndex" = None

    class Meta:
        abstract = True

    def __init__(self) -> None:
        assert self.index_uid is not None and self.index_uid != "", "index_uid is required"

        if self.client is None:
            import paperpilot_common.utils.meili

            self.client = paperpilot_common.utils.meili.meili_client

        super().__init__(self.client.config, uid=self.index_uid, primary_key=self.primary_key)

        if self.class_settings:
            self.update_settings(self._class_settings)

    def __new__(cls, *args, **kwargs):
        """
        singleton
        """
        if cls._instance is None:
            cls._instance = super(BaseIndex, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def _validate_string_list(name: str, value: list[str], allow_empty: bool = True):
        assert isinstance(value, list), f"{name} must be a list"
        assert allow_empty or len(value) > 0, f"{name} must not be empty"
        assert all(isinstance(item, str) for item in value), f"{name} must be a list of string"

    def _validate_class_settings(self):
        self._validate_string_list("displayedAttributes", self.displayed_attributes, allow_empty=False)
        self._validate_string_list(
            "searchableAttributes",
            self.searchable_attributes,
            allow_empty=False,
        )
        self._validate_string_list("filterableAttributes", self.filterable_attributes)
        self._validate_string_list("sortableAttributes", self.sortable_attributes)
        self._validate_string_list("rankingRules", self.ranking_rules, allow_empty=False)
        self._validate_string_list("stopWords", self.stop_words)

        assert isinstance(self.synonyms, dict), "synonyms must be a dict"
        assert all(isinstance(key, str) for key in self.synonyms.keys()), "synonyms keys must be a string"
        assert all(
            isinstance(value, list) for value in self.synonyms.values()
        ), "synonyms values must be a list of string"
        assert all(
            isinstance(item, str) for value in self.synonyms.values() for item in value
        ), "synonyms values must be a list of string"

        assert self.distinct_attribute is None or isinstance(
            self.distinct_attribute, str
        ), "distinctAttribute must be a string or None"

    @property
    def _class_settings(self) -> dict[str, Any]:
        self._validate_class_settings()
        return {
            "displayedAttributes": self.displayed_attributes,
            "searchableAttributes": self.searchable_attributes,
            "filterableAttributes": self.filterable_attributes,
            "sortableAttributes": self.sortable_attributes,
            "rankingRules": self.ranking_rules,
            "stopWords": self.stop_words,
            "synonyms": self.synonyms,
            "distinctAttribute": self.distinct_attribute,
            "faceting": {"maxValuesPerFacet": self.max_values_per_facet},
            "pagination": {"maxTotalHits": self.max_total_hits},
        }


class BaseIndexHelper:
    """
    Index辅助类

    配合BaseIndex使用，结合drf的序列化器操作index内的document

    :var queryset: QuerySet
    :var serializer_class: 序列化器
    :var index_class: Index类

    """

    queryset: QuerySet
    serializer_class: Type[BaseSerializer]
    index_class: Type[BaseIndex]

    class Meta:
        abstract = True

    def __init__(self, auto_update=True):
        """

        :param auto_update: 根据model信号自动更新索引，默认为True
        """
        self.model = self.queryset.model
        self.index = self.index_class()

        if auto_update:
            from django.db.models.signals import post_delete, post_save

            post_save.connect(self.model_save_receiver, sender=self.model)
            post_delete.connect(self.model_delete_receiver, sender=self.model)

    def _to_queryset(
        self,
        objs: Model | PK | list[Model | PK] | QuerySet,
        ignore_default_query_set: bool = False,
    ) -> QuerySet | None:
        """
        将对象、id、id列表、对象列表、QuerySet转换为QuerySet
        """
        if not isinstance(objs, list) and not isinstance(objs, QuerySet):
            # 将单个对象转换为列表
            objs = [objs]

        if isinstance(objs, QuerySet) and not ignore_default_query_set:
            # 限制QuerySet
            objs = objs & self.queryset

        if len(objs) > 0 and isinstance(objs[0], PK):
            if ignore_default_query_set:
                objs = self.model.objects.filter(pk__in=objs)
            else:
                objs = self.queryset.filter(pk__in=objs)

        if len(objs) == 0:
            return None
        return objs

    def upsert_index(
        self,
        objs: Model | PK | list[Model | PK] | QuerySet,
        ignore_default_query_set: bool = False,
    ):
        """
        创建或更新索引

        https://docs.meilisearch.com/reference/api/documents.html#add-or-replace-documents

        :param objs: id、对象、id列表、对象列表、QuerySet
        :param ignore_default_query_set: 忽略默认的query_set限制，默认为False
        :return:
        """
        objs = self._to_queryset(objs, ignore_default_query_set)
        if objs is None:
            return

        serializer = self.serializer_class(objs, many=True)
        data = serializer.data
        self.index.add_documents(data, primary_key=self.index.primary_key)

    def delete_index(
        self,
        objs: Model | PK | list[Model | PK] | QuerySet,
        ignore_default_query_set: bool = True,
    ):
        """
        删除索引

        https://docs.meilisearch.com/reference/api/documents.html#delete-documents-by-batch

        :param objs: id、对象、id列表、对象列表、QuerySet
        :param ignore_default_query_set: 忽略默认的query_set限制，默认为True
        :return:
        """
        objs = self._to_queryset(objs, ignore_default_query_set)
        if objs is None:
            return

        self.index.delete_documents([obj.pk for obj in objs])

    def rebuild_index(self):
        """
        重建索引

        https://docs.meilisearch.com/reference/api/documents.html#delete-all-documents

        :return:
        """
        self.index.delete_all_documents()

        self.index.add_documents(
            self.serializer_class(
                self.queryset,
                many=True,
            ).data,
            primary_key=self.index.primary_key,
        )

    def search(
        self,
        query: str,
        page: int = 1,
        hits_per_page: int = 20,
        filter: str | list | None = None,
        facets: list[str] | None = None,
        attributes_to_retrieve: list[str] | None = None,
        attributes_to_crop: list[str] | None = None,
        crop_length: int | None = None,
        crop_marker: str | None = None,
        attributes_to_highlight: list[str] | None = None,
        highlight_pre_tag: str | None = None,
        highlight_post_tag: str | None = None,
        show_match_positions: bool | None = None,
        sort: list[str] | None = None,
        matching_strategy: str | None = None,
    ) -> SearchResult:
        """
        搜索

        https://docs.meilisearch.com/reference/api/search.html

        :param filter:
        :param query: 关键词
        :param page:
        :param hits_per_page:
        :param filter:
        :param facets:
        :param attributes_to_retrieve:
        :param attributes_to_crop:
        :param crop_length:
        :param crop_marker:
        :param attributes_to_highlight:
        :param highlight_pre_tag:
        :param highlight_post_tag:
        :param show_match_positions:
        :param sort:
        :param matching_strategy:
        :return:
        """
        query_params = {
            "page": page,
            "hitsPerPage": hits_per_page,
        }
        filter and query_params.update({"filter": filter})
        facets and query_params.update({"facetsDistribution": facets})
        attributes_to_retrieve and query_params.update({"attributesToRetrieve": attributes_to_retrieve})
        attributes_to_crop and query_params.update({"attributesToCrop": attributes_to_crop})
        crop_length and query_params.update({"cropLength": crop_length})
        crop_marker and query_params.update({"cropMarker": crop_marker})
        attributes_to_highlight and query_params.update({"attributesToHighlight": attributes_to_highlight})
        highlight_pre_tag and query_params.update({"highlightPreTag": highlight_pre_tag})
        highlight_post_tag and query_params.update({"highlightPostTag": highlight_post_tag})
        show_match_positions and query_params.update({"showMatchPositions": show_match_positions})
        sort and query_params.update({"sort": sort})
        matching_strategy and query_params.update({"matchingStrategy": matching_strategy})

        return SearchResult(self.index.search(query, query_params))

    def search_with_request(self, query: str, request: Request, **kwargs) -> SearchResult:
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        return self.search(query, page=page, hits_per_page=page_size, **kwargs)

    def model_save_receiver(self, instance, **kwargs):
        self.upsert_index(instance)

    def model_delete_receiver(self, instance, **kwargs):
        self.delete_index(instance)
