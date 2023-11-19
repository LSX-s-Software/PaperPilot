from paperpilot_common.grpc.client import GrpcClient
from paperpilot_common.protobuf.project.project_pb2_grpc import (
    ProjectServiceStub,
)


class ProjectClient(GrpcClient):
    """
    项目服务客户端
    """

    server_name = "project"
    stub_cls = ProjectServiceStub

    @property
    def stub(self) -> ProjectServiceStub:
        return super().stub


project_client: ProjectClient = ProjectClient()
