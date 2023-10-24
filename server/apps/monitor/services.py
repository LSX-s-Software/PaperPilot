from datetime import datetime
from typing import Any

import aiodocker
from aiodocker.containers import DockerContainer
from paperpilot_common.helper.field import datetime_to_timestamp
from paperpilot_common.protobuf.monitor.client_pb2 import (
    ClientContainerStatus,
    ClientProjectStatus,
    ClientStatus,
    Status,
)
from paperpilot_common.utils.log import get_logger

from server.config import data


class MonitorClientService:
    logger = get_logger("monitor.client.service")

    host = data["host"]
    containers = data["containers"]
    target_names = [_["name"] for _ in containers]
    project_names = [_["project"] for _ in containers]

    def __init__(self):
        self.docker = aiodocker.Docker()

    async def _process_docker_container(
        self, container: DockerContainer, result: dict[str, Any]
    ):
        container_info = await container.show()
        container_info["Name"] = container_info["Name"].strip("/")
        name: str = container_info["Name"]

        for i, target_name in enumerate(self.target_names):
            if name.startswith(target_name):
                if name not in result:
                    result[self.project_names[i]] = []
                result[self.project_names[i]].append(container_info)

    def _process_container_status(
        self, info: dict[str, Any]
    ) -> ClientContainerStatus:
        status = Status.UNKNOWN
        state = info["State"]
        if state["Status"] == "running":
            health = state.get("Health", None)
            if not health:
                status = Status.RUNNING
            elif health["Status"] == "starting":
                status = Status.STARTING
            elif health["Status"] == "healthy":
                status = Status.HEALTHY
            elif health["Status"] == "unhealthy":
                status = Status.UNHEALTHY
            elif health["Status"] == "none":
                status = Status.RUNNING

        elif state["Status"] == "exited":
            status = Status.STOPPED
        elif state["Status"] == "paused":
            status = Status.STOPPED
        elif state["Status"] == "restarting":
            status = Status.STARTING
        elif state["Status"] == "dead":
            status = Status.STOPPED
        elif state["Status"] == "created":
            status = Status.STARTING
        elif state["Status"] == "removing":
            status = Status.STOPPED

        return ClientContainerStatus(
            id=info["Id"],
            name=info["Name"],
            host=info["Config"]["Hostname"],
            status=status,
        )

    async def get_status(self) -> ClientStatus:
        projects_dict = {}
        docker_containers = await self.docker.containers.list()

        for container in docker_containers:
            await self._process_docker_container(container, projects_dict)

        projects = []
        for project_name, project_containers in projects_dict.items():
            containers = []
            for container in sorted(project_containers, key=lambda x: x["Id"]):
                containers.append(self._process_container_status(container))
            projects.append(
                ClientProjectStatus(
                    project_name=project_name, containers=containers
                )
            )

        return ClientStatus(
            host=self.host,
            projects=projects,
            time=datetime_to_timestamp(datetime.now()),
        )


monitor_service: MonitorClientService = MonitorClientService()
