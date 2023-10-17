import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Type

from google.rpc import status_pb2
from grpc_status import rpc_status

from paperpilot_common.helper.context import context_proxy
from paperpilot_common.protos.common.exce_pb2 import Exec

from .base import GRPC_RESPONSE, BaseInterceptor, ClientCallDetailsType

logger: logging.Logger = logging.getLogger()


class CustomerTopInterceptor(BaseInterceptor):
    def __init__(self, exc_list: Optional[List[Type[Exception]]] = None):
        self.exc_dict: Dict[str, Type[Exception]] = {}
        for key, exc in globals()["__builtins__"].items():
            if inspect.isclass(exc) and issubclass(exc, Exception):
                self.exc_dict[key] = exc

        if exc_list:
            for exc in exc_list:
                if issubclass(exc, Exception):
                    self.exc_dict[exc.__name__] = exc

    def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        call_details: ClientCallDetailsType,
    ) -> GRPC_RESPONSE:
        if call_details.metadata is not None:
            call_details.metadata.append(("request_id", context_proxy.request_id))
        response: GRPC_RESPONSE = method(call_details, request_or_iterator)
        status: Optional[status_pb2.Status] = rpc_status.from_call(response)
        if status:
            for detail in status.details:
                if detail.Is(Exec.DESCRIPTOR):
                    exec_instance: Exec = Exec()
                    detail.Unpack(exec_instance)
                    exec_class: Type[Exception] = self.exc_dict.get(exec_instance.name) or RuntimeError
                    raise exec_class(exec_instance.msg)
                else:
                    raise RuntimeError("Unexpected failure: %s" % detail)
        return response
