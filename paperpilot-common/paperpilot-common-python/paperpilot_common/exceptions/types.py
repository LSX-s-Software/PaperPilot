from datetime import datetime
from typing import List, Optional, TypedDict


class ExceptionInfo(TypedDict, total=True):
    type: str
    value: str
    traceback: List[str]
    inner_type: Optional[str]
    inner_value: Optional[str]


class ExceptionData(TypedDict, total=False):
    eid: Optional[str]
    sentry_id: Optional[str]
    time: datetime
    info: Optional[ExceptionInfo]


ExtraHeaders = TypedDict(
    "ExtraHeaders",
    {
        "WWW-Authenticate": str,
        "Retry-After": str,
    },
    total=False,
)
