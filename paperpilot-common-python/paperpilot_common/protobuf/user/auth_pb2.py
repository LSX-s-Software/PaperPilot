# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: paperpilot_common/protobuf/user/auth.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2

from paperpilot_common.protobuf.user import user_pb2 as paperpilot__common_dot_protobuf_dot_user_dot_user__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n*paperpilot_common/protobuf/user/auth.proto\x12\x04\x61uth\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1bgoogle/protobuf/empty.proto\x1a*paperpilot_common/protobuf/user/user.proto"/\n\x0cLoginRequest\x12\r\n\x05phone\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t"G\n\x05Token\x12\r\n\x05value\x18\x01 \x01(\t\x12/\n\x0b\x65xpire_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp"h\n\rLoginResponse\x12\x1c\n\x04user\x18\x01 \x01(\x0b\x32\x0e.user.UserInfo\x12\x1b\n\x06\x61\x63\x63\x65ss\x18\x02 \x01(\x0b\x32\x0b.auth.Token\x12\x1c\n\x07refresh\x18\x03 \x01(\x0b\x32\x0b.auth.Token"&\n\x13RefreshTokenRequest\x12\x0f\n\x07refresh\x18\x01 \x01(\t"3\n\x14RefreshTokenResponse\x12\x1b\n\x06\x61\x63\x63\x65ss\x18\x01 \x01(\x0b\x32\x0b.auth.Token2\xf2\x01\n\x0b\x41uthService\x12\x30\n\x05Login\x12\x12.auth.LoginRequest\x1a\x13.auth.LoginResponse\x12@\n\x07Refresh\x12\x19.auth.RefreshTokenRequest\x1a\x1a.auth.RefreshTokenResponse\x12\x38\n\x06Logout\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\x12\x35\n\x08Register\x12\x17.user.CreateUserRequest\x1a\x10.user.UserDetailb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "paperpilot_common.protobuf.user.auth_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals["_LOGINREQUEST"]._serialized_start = 158
    _globals["_LOGINREQUEST"]._serialized_end = 205
    _globals["_TOKEN"]._serialized_start = 207
    _globals["_TOKEN"]._serialized_end = 278
    _globals["_LOGINRESPONSE"]._serialized_start = 280
    _globals["_LOGINRESPONSE"]._serialized_end = 384
    _globals["_REFRESHTOKENREQUEST"]._serialized_start = 386
    _globals["_REFRESHTOKENREQUEST"]._serialized_end = 424
    _globals["_REFRESHTOKENRESPONSE"]._serialized_start = 426
    _globals["_REFRESHTOKENRESPONSE"]._serialized_end = 477
    _globals["_AUTHSERVICE"]._serialized_start = 480
    _globals["_AUTHSERVICE"]._serialized_end = 722
# @@protoc_insertion_point(module_scope)
