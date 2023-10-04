from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.urls import include, path
from django.views.generic import RedirectView


def get_attr(self, *args, **kwargs):
    if args[0] == "pk":
        return 0
    return True


class AccessUser:
    has_module_perms = has_perm = __getattr__ = get_attr

    def __str__(self):
        return "User"


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.has_permission = lambda r: setattr(r, "test", AccessUser()) or True


urlpatterns = [
    path("admin/", admin.site.urls),  # admin 后台管理
    # path("api-auth/", include("rest_framework.urls")),  # drf 自带的登录认证
    path(
        "favicon.ico",
        RedirectView.as_view(
            url="https://zq-public-oss.oss-cn-hangzhou.aliyuncs.com/zq-auth/backend/static/static/favorite.ico"
        ),
    ),
]

handler404 = "paperpilot_common.exceptions.views.bad_request"
handler500 = "paperpilot_common.exceptions.views.server_error"

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar  # noqa: WPS433
    from django.conf.urls.static import static  # noqa: WPS433

    urlpatterns = [
        # URLs specific only to django-debug-toolbar:
        path("__debug__/", include(debug_toolbar.urls)),
        *urlpatterns,
        # # Docs:
        # path("docs/schema/", SpectacularAPIView.as_view(), name="schema"),
        # path(
        #     "docs/",
        #     SpectacularSwaggerView.as_view(url_name="schema"),
        #     name="swagger-ui",
        # ),  # swagger接口文档
        # path(
        #     "docs/redoc/",
        #     SpectacularRedocView.as_view(url_name="schema"),
        #     name="redoc",
        # ),  # redoc接口文档
        # Serving media files in development only:
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    ]
