import test.urls

import callback.urls
from starlette.routing import Mount

routes = [
    Mount("/file/test/", routes=test.urls.routes),
    Mount("/callback/", routes=callback.urls.routes),
]
