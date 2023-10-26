import asyncio
import logging
import sys

import grpc.aio
import grpc_health.v1.health as health
from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_reflection.v1alpha import reflection
from paperpilot_common.protobuf.monitor import server_pb2 as monitor_server_pb2
from paperpilot_common.protobuf.paper import paper_pb2
from paperpilot_common.protobuf.project import project_pb2
from paperpilot_common.protobuf.test import test_pb2
from paperpilot_common.protobuf.translation import translation_pb2
from paperpilot_common.protobuf.user import auth_pb2, user_pb2
from paperpilot_common.protobuf.im import im_pb2

logger = logging.getLogger(__name__)


async def serve(addr: str | None = None) -> None:
    if not addr:
        addr = "127.0.0.1:8001"

    server = grpc.aio.server()
    service_names = (
        user_pb2.DESCRIPTOR.services_by_name["UserPublicService"].full_name,
        auth_pb2.DESCRIPTOR.services_by_name["AuthPublicService"].full_name,
        test_pb2.DESCRIPTOR.services_by_name["TestPublicService"].full_name,
        project_pb2.DESCRIPTOR.services_by_name[
            "ProjectPublicService"
        ].full_name,
        paper_pb2.DESCRIPTOR.services_by_name["PaperPublicService"].full_name,
        translation_pb2.DESCRIPTOR.services_by_name[
            "TranslationPublicService"
        ].full_name,
        monitor_server_pb2.DESCRIPTOR.services_by_name[
            "MonitorPublicService"
        ].full_name,
        health_pb2.DESCRIPTOR.services_by_name["Health"].full_name,
        im_pb2.DESCRIPTOR.services_by_name["IMPublicService"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)

    # add health check
    health_servicer = health.aio.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    server.add_insecure_port(addr)
    logger.info("gRPC server listening on %s", addr)
    await server.start()
    await server.wait_for_termination()


def main():
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    addr = None if len(sys.argv) < 2 else sys.argv[1]

    main_task = asyncio.ensure_future(serve(addr))
    try:
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        logger.info("exit...")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
