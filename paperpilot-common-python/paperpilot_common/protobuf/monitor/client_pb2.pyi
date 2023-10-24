"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import google.protobuf.timestamp_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _Status:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _StatusEnumTypeWrapper(
    google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_Status.ValueType], builtins.type
):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    RUNNING: _Status.ValueType  # 0
    STOPPED: _Status.ValueType  # 1
    STARTING: _Status.ValueType  # 2
    HEALTHY: _Status.ValueType  # 3
    UNHEALTHY: _Status.ValueType  # 4
    UNKNOWN: _Status.ValueType  # 5

class Status(_Status, metaclass=_StatusEnumTypeWrapper): ...

RUNNING: Status.ValueType  # 0
STOPPED: Status.ValueType  # 1
STARTING: Status.ValueType  # 2
HEALTHY: Status.ValueType  # 3
UNHEALTHY: Status.ValueType  # 4
UNKNOWN: Status.ValueType  # 5
global___Status = Status

@typing_extensions.final
class ClientStatus(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HOST_FIELD_NUMBER: builtins.int
    PROJECTS_FIELD_NUMBER: builtins.int
    TIME_FIELD_NUMBER: builtins.int
    host: builtins.str
    @property
    def projects(
        self,
    ) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ClientProjectStatus]: ...
    @property
    def time(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    def __init__(
        self,
        *,
        host: builtins.str = ...,
        projects: collections.abc.Iterable[global___ClientProjectStatus] | None = ...,
        time: google.protobuf.timestamp_pb2.Timestamp | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["time", b"time"]) -> builtins.bool: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["host", b"host", "projects", b"projects", "time", b"time"]
    ) -> None: ...

global___ClientStatus = ClientStatus

@typing_extensions.final
class ClientProjectStatus(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    PROJECT_NAME_FIELD_NUMBER: builtins.int
    CONTAINERS_FIELD_NUMBER: builtins.int
    project_name: builtins.str
    @property
    def containers(
        self,
    ) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ClientContainerStatus]: ...
    def __init__(
        self,
        *,
        project_name: builtins.str = ...,
        containers: collections.abc.Iterable[global___ClientContainerStatus] | None = ...,
    ) -> None: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["containers", b"containers", "project_name", b"project_name"]
    ) -> None: ...

global___ClientProjectStatus = ClientProjectStatus

@typing_extensions.final
class ClientContainerStatus(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    HOST_FIELD_NUMBER: builtins.int
    STATUS_FIELD_NUMBER: builtins.int
    id: builtins.str
    name: builtins.str
    host: builtins.str
    status: global___Status.ValueType
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        name: builtins.str = ...,
        host: builtins.str = ...,
        status: global___Status.ValueType = ...,
    ) -> None: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["host", b"host", "id", b"id", "name", b"name", "status", b"status"]
    ) -> None: ...

global___ClientContainerStatus = ClientContainerStatus
