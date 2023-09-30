# 自定义返回格式
from typing import Any, Mapping, Optional

from rest_framework.renderers import JSONRenderer

from paperpilot_common.response import ApiResponse
from paperpilot_common.response.types import ApiExceptionResponse


class CustomRenderer(JSONRenderer):
    # 重构render方法
    def render(
        self,
        data: Any,
        accepted_media_type: Optional[str] = None,
        renderer_context: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        if renderer_context:
            response: ApiExceptionResponse = renderer_context["response"]
            try:  # 记录请求数据，便于日志处理
                request_data = renderer_context["request"].data
                response.api_request_data = request_data
            except Exception:
                pass

            if not response.exception:  # 如果不是异常
                data = ApiResponse(data=data).__dict__()  # 将data包装成ApiResponse

        return super().render(data, accepted_media_type, renderer_context)
