from paperpilot_common.grpc.client import GrpcClient
from paperpilot_common.protobuf.paper.paper_pb2_grpc import PaperServiceStub

from server import settings


class PaperClient(GrpcClient):
    """
    论文服务客户端
    """

    server_name = "paper"
    server_host = settings.GRPC_CLIENT["clients"]["paper"]["server_host"]
    stub_cls = PaperServiceStub

    @property
    def stub(self) -> PaperServiceStub:
        return super().stub


paper_client: PaperClient = PaperClient()
