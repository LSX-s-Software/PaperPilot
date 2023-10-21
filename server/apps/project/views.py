from paperpilot_common.exceptions import ApiException
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger
from project.models import Project
from project.services import project_service
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse


def handle_api_exception(exc: ApiException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.response_type.status_code,
        content={
            "code": exc.response_type.code,
            "detail": exc.detail,
            "msg": exc.msg,
        },
    )


class InvitationView(HTTPEndpoint):
    logger = get_logger("project.invitation")

    async def get(self, request):
        invite_code = request.query_params.get("invite_code", None)

        if not invite_code:
            return handle_api_exception(
                ApiException(ResponseType.ParamEmpty, msg="邀请码为空", record=True)
            )

        if not len(invite_code) == 32:
            return handle_api_exception(
                ApiException(
                    ResponseType.ParamError, msg="邀请码格式错误", record=True
                )
            )

        project = await Project.objects.filter(invite_code=invite_code).afirst()

        if not project:
            return handle_api_exception(
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
