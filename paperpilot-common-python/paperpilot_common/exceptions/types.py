from datetime import datetime
from typing import List, Optional, TypedDict


class ExceptionInfo(TypedDict, total=True):
    type: str
    msg: str
    info: str
    stack: List[str]


class ExceptionData(TypedDict, total=False):
    eid: Optional[str]
    time: datetime
    exception: Optional[ExceptionInfo]


ExtraHeaders = TypedDict(
    "ExtraHeaders",
    {
        "WWW-Authenticate": str,
        "Retry-After": str,
    },
    total=False,
)
