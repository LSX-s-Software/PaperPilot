from django.http import HttpRequest, JsonResponse

from paperpilot_common.response import ApiResponse, ResponseType


def bad_request(request: HttpRequest, exception: Exception) -> JsonResponse:
    """
    404 页面

    在 url.py 中设定 handler404 为此函数

    """
    return ApiResponse(ResponseType.APINotFound, "您访问的页面不存在").to_json_response()


def server_error(request: HttpRequest) -> JsonResponse:
    """
    500 页面

    在 url.py 中设定 handler500 为此函数

    """
    # TODO 结合异常处理(记录日志)
    return ApiResponse(ResponseType.ServerError).to_json_response()
