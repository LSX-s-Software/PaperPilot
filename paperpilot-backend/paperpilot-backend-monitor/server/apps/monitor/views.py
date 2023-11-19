from starlette.endpoints import HTTPEndpoint
from starlette.responses import Response

from server.apps.monitor.services import monitor_service


class StatusSvgView(HTTPEndpoint):
    async def get(self, request):
        # no cache
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }

        return Response(
            status_code=200,
            media_type="image/svg+xml",
            content=await monitor_service.get_status_svg(),
            headers=headers,
        )
