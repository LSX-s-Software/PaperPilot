from callback.views import CallbackUserAvatarView
from starlette.routing import Route

routes = [
    Route("/user/avatar/", CallbackUserAvatarView),
]
