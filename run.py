import asyncio
import sys

import grpc.aio
import grpc_health.v1.health as health
from grpc_health.v1 import health_pb2_grpc
from grpc_reflection.v1alpha import reflection
from paperpilot_common.utils.log import get_logger

import server.apps.monitor.urls as monitor
from server.utils.logging_handler import init_logging
from server.utils.trace import init_trace

logger = get_logger("server")


async def serve(addr: str | None = None) -> None:
    if not addr:
        addr = "127.0.0.1:8001"

    server = grpc.aio.server()
    service_names = []
    service_names.extend(monitor.grpc_hook(server))

    # add reflection
    service_names.append(reflection.SERVICE_NAME)
    reflection.enable_server_reflection(service_names, server)

    # add health check
    health_servicer = health.aio.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    server.add_insecure_port(addr)
    logger.info(f"gRPC server listening on {addr}")
    await server.start()
    await server.wait_for_termination()


def main():
    init_logging()
    init_trace("paperpilot-backend-monitor")

    addr = None if len(sys.argv) < 2 else sys.argv[1]

    loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(serve(addr))
    try:
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        logger.info("exit...")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
