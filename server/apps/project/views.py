from pathlib import Path

from paperpilot_common.exceptions import ApiException
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger
from project.models import Project
from project.services import project_service
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse, JSONResponse


class InvitationView(HTTPEndpoint):
    logger = get_logger("project.invitation")

    def handle_api_exception(self, exc: ApiException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.response_type.status_code,
            content={
                "code": exc.response_type.code,
                "detail": exc.detail,
                "msg": exc.msg,
            },
        )

    async def get(self, request):
        invite_code = request.query_params.get("invite_code", None)

        if not invite_code:
            return self.handle_api_exception(
                ApiException(ResponseType.ParamEmpty, msg="邀请码为空", record=True)
            )

        if not len(invite_code) == 32:
            return self.handle_api_exception(
                ApiException(
                    ResponseType.ParamError, msg="邀请码格式错误", record=True
                )
            )

        project = await Project.objects.filter(invite_code=invite_code).afirst()

        if not project:
            return self.handle_api_exception(
                ApiException(
                    ResponseType.ParamError,
                    msg="邀请码错误",
                    detail="您输入的邀请码不存在，请检查后重试",
                )
            )

        project = await project_service._get_project_info(project=project)

        owner = None

        for member in project.members:
            if member.id == project.owner_id:
                owner = member
                break

        return JSONResponse(
            {
                "name": project.name,
                "description": project.description,
                "owner": {
                    "username": owner.username,
                    "avatar": owner.avatar,
                },
                "member": [
                    member.avatar
                    for member in project.members
                    if member.id != owner.id
                ],
            }
        )


class InvitationHtmlView(HTTPEndpoint):
    logger = get_logger("project.invitation-html")
    TEMPLATES = Path(__file__).parent / "templates"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(
            self.TEMPLATES / "invite-error.html", "r", encoding="utf-8"
        ) as f:
            self.error_html = f.read()
        with open(self.TEMPLATES / "invite.html", "r", encoding="utf-8") as f:
            self.invite_html = f.read()

    def handle_api_exception_html(self, exc: ApiException) -> HTMLResponse:
        return HTMLResponse(
            status_code=exc.response_type.status_code,
            content=self.error_html.replace("{{error}}", exc.detail),
        )

    async def get(self, request):
        invite_code = request.query_params.get("invitation", None)

        if not invite_code:
            return self.handle_api_exception_html(
                ApiException(
                    ResponseType.ParamEmpty, msg="邀请码为空", detail="您未输入邀请码，请重试"
                )
            )

        if not len(invite_code) == 32:
            return self.handle_api_exception_html(
                ApiException(
                    ResponseType.ParamError,
                    msg="邀请码格式错误",
                    detail="您输入的邀请码格式错误，请检查后重试",
                )
            )

        project = await Project.objects.filter(invite_code=invite_code).afirst()

        if not project:
            return self.handle_api_exception_html(
                ApiException(
                    ResponseType.ParamError,
                    msg="邀请码错误",
                    detail="您输入的邀请码不存在，请检查后重试",
                )
            )

        project = await project_service._get_project_info(project=project)

        owner = None

        for member in project.members:
            if member.id == project.owner_id:
                owner = member
                break

        avatar_list = [
            f"<li><img src='{owner.avatar}' alt='Owner Avatar'></li>"
        ]

        for member in project.members:
            if member.id != owner.id:
                avatar_list.append(
                    f"<li><img src='{member.avatar}' alt='Member Avatar'></li>"
                )

        content = (
            self.invite_html.replace("{{owner_username}}", owner.username)
            .replace("{{project_name}}", project.name)
            .replace("{{project_description}}", project.description)
            .replace("{{members_list}}", "".join(avatar_list))
            .replace("{{invite_code}}", invite_code)
            .replace("{{og_description}}", project.description[:65])
        )

        return HTMLResponse(
            status_code=200,
            content=content,
        )
