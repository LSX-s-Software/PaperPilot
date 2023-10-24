from paperpilot_common.grpc.client import GrpcClient
from paperpilot_common.protobuf.monitor.client_pb2_grpc import (
    MonitorClientServiceStub,
)

from server.config import data


class MonitorClient(GrpcClient):
    """
    监控服务采集客户端
    """

    stub_cls = MonitorClientServiceStub

    def __init__(self, server: str):
        self.server_name = f"monitor.{server}"
        self.server_host = server
        super().__init__()

    @property
    def stub(self) -> MonitorClientServiceStub:
        return super().stub

    def _connect(self):
        import grpc.aio
        from grpc import ssl_channel_credentials
        from paperpilot_common.grpc.client.wrapper import StubTraceWrapper

        self.channel = grpc.aio.secure_channel(
            self.server_host, ssl_channel_credentials()
        )
        self.logger.info(
            f"connect to {self.server_name} server {self.server_host}"
        )
        self._stub = StubTraceWrapper(self.stub_cls(self.channel))


def init_clients() -> list[MonitorClient]:
    servers = data["monitor_clients"]
    clients = []
    for server in servers:
        clients.append(MonitorClient(server))

    return clients


monitor_clients = init_clients()
