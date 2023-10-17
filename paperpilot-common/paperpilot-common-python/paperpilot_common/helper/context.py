from contextvars import ContextVar, Token
from typing import Any, Dict, Optional

_request_context: ContextVar[Dict[str, Any]] = ContextVar("request_context", default={})


class Context(object):
    package: str
    service: str
    method: str
    method_name: str
    metadata_dict: dict
    inited: bool
    req_id: str
    grpc_type: str

    def __getattr__(self, key: str) -> Any:
        value: Any = _request_context.get().get(key)
        return value

    def __setattr__(self, key: str, value: Any) -> None:
        _request_context.get()[key] = value


class WithContext(Context):
    def __init__(self) -> None:
        self._token: Optional[Token] = None

    def __enter__(self) -> "WithContext":
        if self._token:
            self._token = _request_context.set({})
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._token:
            _request_context.reset(self._token)


context_proxy: Context = Context()
