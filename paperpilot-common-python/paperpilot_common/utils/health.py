from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from starlette.routing import Route

from paperpilot_common.utils.log import get_logger


class HealthView(HTTPEndpoint):
    logger = get_logger("health.view")

    async def get(self, request):
        return JSONResponse({})


routes = [
    Route("/", HealthView),
]
