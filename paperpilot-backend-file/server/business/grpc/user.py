from paperpilot_common.grpc.client import GrpcClient
from paperpilot_common.protobuf.user.user_pb2_grpc import UserServiceStub

from server import settings


class UserClient(GrpcClient):
    """
    用户服务客户端
    """

    server_name = "user"
    server_host = settings.GRPC_CLIENT["clients"]["user"]["server_host"]
    stub_cls = UserServiceStub

    @property
    def stub(self) -> UserServiceStub:
        return super().stub


user_client: UserClient = UserClient()
