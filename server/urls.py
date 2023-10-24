from starlette.routing import Mount
from paperpilot_common.utils import health

import test.urls
import callback.urls

routes = [
    Mount("/health/", routes=health.routes),
    Mount("/file/test/", routes=test.urls.routes),
    Mount("/callback/", routes=callback.urls.routes),
]
