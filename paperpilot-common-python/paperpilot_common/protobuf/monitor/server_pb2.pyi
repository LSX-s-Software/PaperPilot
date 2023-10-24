"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message
import google.protobuf.timestamp_pb2
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class ServerStatus(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HOST_COUNT_FIELD_NUMBER: builtins.int
    PROJECTS_FIELD_NUMBER: builtins.int
    TIME_FIELD_NUMBER: builtins.int
    host_count: builtins.int
    @property
    def projects(
        self,
    ) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ProjectStatus]: ...
    @property
    def time(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    def __init__(
        self,
        *,
        host_count: builtins.int = ...,
        projects: collections.abc.Iterable[global___ProjectStatus] | None = ...,
        time: google.protobuf.timestamp_pb2.Timestamp | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["time", b"time"]) -> builtins.bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal["host_count", b"host_count", "projects", b"projects", "time", b"time"],
    ) -> None: ...

global___ServerStatus = ServerStatus

@typing_extensions.final
class ProjectStatus(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    DESCRIPTION_FIELD_NUMBER: builtins.int
    HEALTHY_COUNT_FIELD_NUMBER: builtins.int
    TOTAL_COUNT_FIELD_NUMBER: builtins.int
    id: builtins.str
    name: builtins.str
    description: builtins.str
    healthy_count: builtins.int
    total_count: builtins.int
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        name: builtins.str = ...,
        description: builtins.str = ...,
        healthy_count: builtins.int = ...,
        total_count: builtins.int = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "description",
            b"description",
            "healthy_count",
            b"healthy_count",
            "id",
            b"id",
            "name",
            b"name",
            "total_count",
            b"total_count",
        ],
    ) -> None: ...

global___ProjectStatus = ProjectStatus
