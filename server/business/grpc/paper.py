from paperpilot_common.grpc.client import GrpcClient
from paperpilot_common.protobuf.paper.paper_pb2_grpc import PaperServiceStub


class PaperClient(GrpcClient):
    """
    论文服务客户端
    """

    server_name = "paper"
    server_host = "localhost"
    stub_cls = PaperServiceStub

    @property
    def stub(self) -> PaperServiceStub:
        return super().stub


paper_client: PaperClient = PaperClient()
