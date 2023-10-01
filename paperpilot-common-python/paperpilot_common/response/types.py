from typing import Dict, List, TypedDict, Union

from rest_framework.response import Response

from paperpilot_common.exceptions import ApiException

JSONVal = Union[None, bool, str, float, int, List["JSONVal"], Dict[str, "JSONVal"]]


class ResponseData(TypedDict, total=True):
    code: str
    detail: str
    msg: str
    data: JSONVal


class ApiExceptionResponse(Response):
    api_request_data: Dict[str, JSONVal]
    exception_data: ApiException
    exception: bool
