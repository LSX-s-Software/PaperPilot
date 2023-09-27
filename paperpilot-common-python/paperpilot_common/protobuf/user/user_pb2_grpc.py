# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

from paperpilot_common.protobuf.user import user_pb2 as paperpilot__common_dot_protobuf_dot_user_dot_user__pb2


class UserServiceStub(object):
    """用户服务接口"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetUserInfo = channel.unary_unary(
            "/user.UserService/GetUserInfo",
            request_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserId.SerializeToString,
            response_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserInfo.FromString,
        )
        self.GetUserDetail = channel.unary_unary(
            "/user.UserService/GetUserDetail",
            request_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserId.SerializeToString,
            response_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.FromString,
        )
        self.ListUserInfo = channel.unary_unary(
            "/user.UserService/ListUserInfo",
            request_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserIdList.SerializeToString,
            response_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserInfoList.FromString,
        )
        self.UpdateUserAvatar = channel.unary_unary(
            "/user.UserService/UpdateUserAvatar",
            request_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UpdateUserAvatarRequest.SerializeToString,
            response_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.FromString,
        )


class UserServiceServicer(object):
    """用户服务接口"""

    def GetUserInfo(self, request, context):
        """获取指定ID用户简要信息"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetUserDetail(self, request, context):
        """获取指定ID用户详细信息"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def ListUserInfo(self, request, context):
        """批量获取用户简要信息"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def UpdateUserAvatar(self, request, context):
        """更新用户头像"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_UserServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetUserInfo": grpc.unary_unary_rpc_method_handler(
            servicer.GetUserInfo,
            request_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserId.FromString,
            response_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserInfo.SerializeToString,
        ),
        "GetUserDetail": grpc.unary_unary_rpc_method_handler(
            servicer.GetUserDetail,
            request_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserId.FromString,
            response_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.SerializeToString,
        ),
        "ListUserInfo": grpc.unary_unary_rpc_method_handler(
            servicer.ListUserInfo,
            request_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserIdList.FromString,
            response_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserInfoList.SerializeToString,
        ),
        "UpdateUserAvatar": grpc.unary_unary_rpc_method_handler(
            servicer.UpdateUserAvatar,
            request_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UpdateUserAvatarRequest.FromString,
            response_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler("user.UserService", rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class UserService(object):
    """用户服务接口"""

    @staticmethod
    def GetUserInfo(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/user.UserService/GetUserInfo",
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserId.SerializeToString,
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetUserDetail(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/user.UserService/GetUserDetail",
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserId.SerializeToString,
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def ListUserInfo(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/user.UserService/ListUserInfo",
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserIdList.SerializeToString,
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserInfoList.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def UpdateUserAvatar(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/user.UserService/UpdateUserAvatar",
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UpdateUserAvatarRequest.SerializeToString,
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )


class UserPublicServiceStub(object):
    """用户公开接口"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetUserInfo = channel.unary_unary(
            "/user.UserPublicService/GetUserInfo",
            request_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserId.SerializeToString,
            response_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserInfo.FromString,
        )
        self.GetCurrentUser = channel.unary_unary(
            "/user.UserPublicService/GetCurrentUser",
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.FromString,
        )
        self.UpdateUser = channel.unary_unary(
            "/user.UserPublicService/UpdateUser",
            request_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UpdateUserRequest.SerializeToString,
            response_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.FromString,
        )
        self.UploadUserAvatar = channel.unary_unary(
            "/user.UserPublicService/UploadUserAvatar",
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UploadUserAvatarResponse.FromString,
        )


class UserPublicServiceServicer(object):
    """用户公开接口"""

    def GetUserInfo(self, request, context):
        """获取指定ID用户简要信息"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetCurrentUser(self, request, context):
        """获取当前用户信息"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def UpdateUser(self, request, context):
        """更新用户信息"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def UploadUserAvatar(self, request, context):
        """上传用户头像"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_UserPublicServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetUserInfo": grpc.unary_unary_rpc_method_handler(
            servicer.GetUserInfo,
            request_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserId.FromString,
            response_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserInfo.SerializeToString,
        ),
        "GetCurrentUser": grpc.unary_unary_rpc_method_handler(
            servicer.GetCurrentUser,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.SerializeToString,
        ),
        "UpdateUser": grpc.unary_unary_rpc_method_handler(
            servicer.UpdateUser,
            request_deserializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UpdateUserRequest.FromString,
            response_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.SerializeToString,
        ),
        "UploadUserAvatar": grpc.unary_unary_rpc_method_handler(
            servicer.UploadUserAvatar,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UploadUserAvatarResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler("user.UserPublicService", rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class UserPublicService(object):
    """用户公开接口"""

    @staticmethod
    def GetUserInfo(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/user.UserPublicService/GetUserInfo",
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserId.SerializeToString,
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetCurrentUser(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/user.UserPublicService/GetCurrentUser",
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def UpdateUser(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/user.UserPublicService/UpdateUser",
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UpdateUserRequest.SerializeToString,
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UserDetail.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def UploadUserAvatar(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/user.UserPublicService/UploadUserAvatar",
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            paperpilot__common_dot_protobuf_dot_user_dot_user__pb2.UploadUserAvatarResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
