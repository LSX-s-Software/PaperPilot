from paperpilot_common.grpc.client import GrpcClient
from paperpilot_common.protobuf.user.user_pb2_grpc import UserServiceStub


class UserClient(GrpcClient):
    """
    用户服务客户端
    """

    server_name = "user"
    stub_cls = UserServiceStub

    @property
    def stub(self) -> UserServiceStub:
        return super().stub


user_client: UserClient = UserClient()
