from callback.views import CallbackPaperFileView, CallbackUserAvatarView
from starlette.routing import Route

routes = [
    Route("/user/avatar/", CallbackUserAvatarView),
    Route("/paper/file/", CallbackPaperFileView),
]
