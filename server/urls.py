import test.urls

import callback.urls
from paperpilot_common.utils import health
from starlette.routing import Mount

routes = [
    Mount("/health/", routes=health.routes),
    Mount("/file/test/", routes=test.urls.routes),
    Mount("/callback/", routes=callback.urls.routes),
]
