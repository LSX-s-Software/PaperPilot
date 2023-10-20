from paperpilot_common.utils.log import get_logger
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from server.utils import timezone


class TestView(HTTPEndpoint):
    logger = get_logger("test.view")

    async def get(self, request):
        self.logger.debug("test")
        return JSONResponse(
            {
                "message": "success",
                "time": timezone.now().astimezone().isoformat(),
            }
        )

    async def post(self, request):
        self.logger.debug("test post")
        return JSONResponse(
            {
                "message": "success",
                "time": timezone.now().astimezone().isoformat(),
            }
        )
