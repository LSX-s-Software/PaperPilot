import grpc.aio

from paperpilot_common.utils.log import get_logger

from .wrapper import StubTraceWrapper


class GrpcClient:
    server_name: str
    server_host: str
    stub_cls: type
    _stub: object = None
    channel: grpc.aio.Channel | None

    def __init__(self):
        assert self.server_name, "server_name must be set"
        assert self.stub_cls, "stub_cls must be set"
        if not hasattr(self, "server_host"):
            from ..config import clients

            self.server_host = clients[self.server_name]["server_host"]

        self.channel = None
        self._stub = None
        self.logger = get_logger(f"grpc.client.{self.server_name}")

    def _connect(self):
        self.channel = grpc.aio.insecure_channel(self.server_host)
        self.logger.info(f"connect to {self.server_name} server {self.server_host}")
        self._stub = StubTraceWrapper(self.stub_cls(self.channel))

    @property
    def stub(self):
        if self._stub is None:
            self._connect()
        return self._stub

    def connect(self):
        self._connect()

    async def close(self):
        if self.channel:
            await self.channel.close(None)
            self.logger.debug(f"close {self.server_name}")

    def __repr__(self):
        return f"<GrpcClient {self.server_name}>"

    def __str__(self):
        return self.server_name
