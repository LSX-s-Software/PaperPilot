from test.views import TestView

from starlette.routing import Route

routes = [
    Route("/", TestView),
]
