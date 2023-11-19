from paperpilot_common.grpc.client import GrpcClient
from paperpilot_common.protobuf.im.im_pb2_grpc import IMServiceStub


class IMClient(GrpcClient):
    """
    即时通讯服务客户端
    """

    server_name = "im"
    stub_cls = IMServiceStub

    @property
    def stub(self) -> IMServiceStub:
        return super().stub


im_client: IMClient = IMClient()
