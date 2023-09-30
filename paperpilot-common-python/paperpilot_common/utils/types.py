import abc
import collections.abc
import typing
from typing import Dict, List, Union

import grpc
import grpc.aio

_T = typing.TypeVar("_T")


class _MaybeAsyncIterator(collections.abc.AsyncIterator[_T], collections.abc.Iterator[_T], metaclass=abc.ABCMeta):
    pass


class _ServicerContext(grpc.ServicerContext, grpc.aio.ServicerContext):
    pass


SimpleValue = Union[str, int, bool, float]

JSONValue = Union[None, SimpleValue, List["JSONVal"], Dict[str, "JSONVal"]]  # noqa: F821
