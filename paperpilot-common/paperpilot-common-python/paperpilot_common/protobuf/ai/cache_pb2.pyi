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
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _Role:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _RoleEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_Role.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    USER: _Role.ValueType  # 0
    ASSISTANT: _Role.ValueType  # 1

class Role(_Role, metaclass=_RoleEnumTypeWrapper): ...

USER: Role.ValueType  # 0
ASSISTANT: Role.ValueType  # 1
global___Role = Role

@typing_extensions.final
class Message(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ROLE_FIELD_NUMBER: builtins.int
    CONTENT_FIELD_NUMBER: builtins.int
    role: global___Role.ValueType
    content: builtins.str
    def __init__(
        self,
        *,
        role: global___Role.ValueType = ...,
        content: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["content", b"content", "role", b"role"]) -> None: ...

global___Message = Message

@typing_extensions.final
class Chat(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    MESSAGES_FIELD_NUMBER: builtins.int
    @property
    def messages(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Message]: ...
    def __init__(
        self,
        *,
        messages: collections.abc.Iterable[global___Message] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["messages", b"messages"]) -> None: ...

global___Chat = Chat