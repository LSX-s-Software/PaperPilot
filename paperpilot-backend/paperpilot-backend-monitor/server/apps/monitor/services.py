from datetime import datetime

import google.protobuf.empty_pb2
from paperpilot_common.helper.field import datetime_to_timestamp
from paperpilot_common.protobuf.monitor.client_pb2 import (
    ClientContainerStatus,
    ClientStatus,
    Status,
)
from paperpilot_common.protobuf.monitor.server_pb2 import (
    ProjectStatus,
    ServerStatus,
)
from paperpilot_common.utils.log import get_logger

from server.business.grpc.monitor_client import monitor_clients
from server.business.svg import SvgDrawer
from server.config import data


class MonitorPublicService:
    logger = get_logger("monitor.server.service")

    def __init__(self):
        self.projects = {_["id"]: _ for _ in data["projects"]}

    async def get_client_status(self) -> list[ClientStatus]:
        result = []
        for client in monitor_clients:
            try:
                result.append(
                    await client.stub.GetStatus(
                        google.protobuf.empty_pb2.Empty, timeout=0.8
                    )
                )
            except Exception as e:
                self.logger.error(f"get client status error: {e}")

        return result

    async def get_status(self) -> ServerStatus:
        client_status = await self.get_client_status()
        projects_info: dict[str, list[ClientContainerStatus]] = {}

        for client in client_status:
            for project in client.projects:
                project_name = project.project_name
                if project_name not in projects_info:
                    projects_info[project_name] = []

                projects_info[project_name].extend(project.containers)

        projects = []

        for project_name, containers in projects_info.items():
            project = self.projects.get(project_name, None)

            if not project:
                project = {
                    "id": project_name,
                    "name": project_name,
                    "description": "",
                }

            projects.append(
                ProjectStatus(
                    id=project["id"],
                    name=project["name"],
                    description=project["description"],
                    healthy_count=len(
                        [_ for _ in containers if _.status == Status.HEALTHY]
                    ),
                    total_count=len(containers),
                )
            )

        return ServerStatus(
            host_count=len(client_status),
            projects=projects,
            time=datetime_to_timestamp(datetime.now()),
        )

    async def get_status_svg(self) -> str:
        client_status = await self.get_client_status()
        projects_info: dict[str, list[ClientContainerStatus]] = {}

        for client in client_status:
            for project in client.projects:
                project_name = project.project_name
                if project_name not in projects_info:
                    projects_info[project_name] = []

                projects_info[project_name].extend(project.containers)

        projects = []

        for project_name, containers in projects_info.items():
            project = self.projects.get(project_name, None)

            if not project:
                project = {
                    "id": project_name,
                    "name": project_name,
                    "description": "",
                }

            projects.append(
                dict(
                    id=project["id"],
                    name=project["name"],
                    description=project["description"],
                    healthy_count=len(
                        [_ for _ in containers if _.status == Status.HEALTHY]
                    ),
                    total_count=len(containers),
                )
            )

        data = dict(
            host_count=len(client_status),
            projects=projects,
            time=datetime.now(),
        )

        drawer = SvgDrawer(data)

        return drawer.draw()


monitor_service: MonitorPublicService = MonitorPublicService()
