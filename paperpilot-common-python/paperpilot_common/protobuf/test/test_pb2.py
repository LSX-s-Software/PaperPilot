# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: paperpilot_common/protobuf/test/test.proto
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
    b'\n*paperpilot_common/protobuf/test/test.proto\x12\x04test\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a*paperpilot_common/protobuf/user/user.proto"T\n\nTestResult\x12(\n\x04time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x1c\n\x04user\x18\x02 \x01(\x0b\x32\x0e.user.UserInfo2E\n\x11TestPublicService\x12\x30\n\x04Test\x12\x16.google.protobuf.Empty\x1a\x10.test.TestResultb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "paperpilot_common.protobuf.test.test_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals["_TESTRESULT"]._serialized_start = 158
    _globals["_TESTRESULT"]._serialized_end = 242
    _globals["_TESTPUBLICSERVICE"]._serialized_start = 244
    _globals["_TESTPUBLICSERVICE"]._serialized_end = 313
# @@protoc_insertion_point(module_scope)
