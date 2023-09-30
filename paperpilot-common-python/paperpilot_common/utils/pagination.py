from rest_framework.pagination import PageNumberPagination


class GlobalPageNumberPagination(PageNumberPagination):
    """
    自定义分页
    """

    def __init__(self):
        super(GlobalPageNumberPagination, self).__init__()
        # TODO config化参数，嵌套类进行参数局部定义
        self.page_size_query_param = "page_size"
        self.page_size = 20
        self.max_page_size = 200
