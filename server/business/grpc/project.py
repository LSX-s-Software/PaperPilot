from google.protobuf.wrappers_pb2 import BoolValue
from paperpilot_common.grpc.client import GrpcClient
from paperpilot_common.protobuf.project.project_pb2 import (
    CheckUserJoinedProjectRequest,
)
from paperpilot_common.protobuf.project.project_pb2_grpc import (
    ProjectServiceStub,
)
from paperpilot_common.utils.log import get_logger


class FakeStub:
    logger = get_logger("grpc.client.project.fake_stub")

    async def CheckUserJoinedProject(
        self, request: CheckUserJoinedProjectRequest
    ) -> BoolValue:
        self.logger.info(
            f"Check user {request.user_id} joined project {request.project_id}"
        )
        return BoolValue(value=True)


fake_stub = FakeStub()


class ProjectClient(GrpcClient):
    """
    项目服务客户端
    """

    server_name = "project"
    stub_cls = ProjectServiceStub

    @property
    def stub(self) -> ProjectServiceStub:
        # return super().stub
        return fake_stub


project_client: ProjectClient = ProjectClient()
