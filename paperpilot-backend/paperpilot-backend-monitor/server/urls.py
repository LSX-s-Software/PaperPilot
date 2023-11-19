from paperpilot_common.utils import health
from starlette.routing import Mount

import server.apps.monitor.urls as monitor

routes = [
    Mount("/health/", routes=health.routes),
    Mount("/status/", routes=monitor.routes),
]
