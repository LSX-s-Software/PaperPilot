from datetime import datetime
from typing import Dict, List, Optional, TypedDict, Union

from paperpilot_common.response.types import JSONVal

HeaderContent = Union[str, List["HeaderContent"], Dict[str, "HeaderContent"]]
HeaderDict = Dict[str, HeaderContent]


class FileDataDict(TypedDict, total=True):
    name: str
    size: int
    content_type: str
    content_type_extra: str


class RequestLogDict(TypedDict, total=True):
    user: Optional[int]
    ip: str
    method: str
    url: str
    headers: HeaderDict
    content_type: str
    query_param: Dict[str, JSONVal]
    request_body: Dict[str, JSONVal]
    file_data: Dict[str, FileDataDict]
    response: JSONVal
    status_code: int
    execution_time: Optional[float]
    create_time: datetime


class ExceptionLogDict(RequestLogDict, total=True):
    exp_id: Optional[str]
    event_id: Optional[str]
    exception_type: str
    exception_msg: str
    exception_info: str
    stack_info: List[str]
