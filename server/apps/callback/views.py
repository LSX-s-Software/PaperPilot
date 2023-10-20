import abc
from urllib.parse import parse_qs
from uuid import UUID

import pytz
from paperpilot_common.exceptions import ApiException
from paperpilot_common.middleware.server.context import trace_id_context
from paperpilot_common.oss.callback import OssCallbackChecker
from paperpilot_common.protobuf.paper.paper_pb2 import (
    PaperDetail,
    UpdateAttachmentRequest,
)
from paperpilot_common.protobuf.user.user_pb2 import (
    UpdateUserAvatarRequest,
    UserDetail,
)
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from server.business.grpc.paper import paper_client
from server.business.grpc.user import user_client


class BaseCallbackView(HTTPEndpoint):
    logger_name = "callback.base_view"
    checker = OssCallbackChecker()

    def __init__(self, *args, **kwargs):
        self.logger = get_logger(self.logger_name)
        super().__init__(*args, **kwargs)

    async def post(self, request):
        self.logger.debug(f"callback, request: {request}")

        query_string = "&".join(
            [f"{k}={v}" for k, v in request.query_params.items()]
        )

        if not await self.checker.check_callback_signature(
            headers=request.headers,
            body=await request.body(),
            query_string=query_string,
            path_info=request.url.path,
        ):
            raise ApiException(
                ResponseType.PermissionDenied, "OSS回调签名检验失败", record=True
            )

        query = dict(request.query_params)
        body = {
            k.decode(): v[0].decode()
            for k, v in parse_qs(await request.body()).items()
        }

        trace_id = UUID(body["trace_id"])
        trace_id_context.set(trace_id)

        return await self.handle(query, body, request)

    @abc.abstractmethod
    async def handle(
        self, query: dict[str, str], body: dict[str, str], request: Request
    ) -> JSONResponse:
        """
        处理回调

        :param query: query参数
        :param body: body参数
        :param request: 请求对象
        :return: JSON响应
        """
        raise NotImplementedError


class CallbackUserAvatarView(BaseCallbackView):
    logger_name = "callback.user.avatar.view"
    user_service = user_client.stub

    async def handle(
        self, query: dict[str, str], body: dict[str, str], request: Request
    ) -> JSONResponse:
        user_id = query.get("user_id", None)
        if user_id is None:
            raise ApiException(
                ResponseType.ParamEmpty, "user_id不能为空", record=True
            )

        key = body.get("object", None)
        if key is None:
            raise ApiException(
                ResponseType.ParamEmpty, "object不能为空", record=True
            )

        self.logger.debug(
            f"callback update user avatar, user_id: {user_id}, object: {key}"
        )

        user_detail: UserDetail = await self.user_service.UpdateUserAvatar(
            UpdateUserAvatarRequest(
                id=user_id,
                avatar=key,
            )
        )

        return JSONResponse(
            {
                "id": user_detail.id,
                "username": user_detail.username,
                "phone": user_detail.phone,
                "avatar": user_detail.avatar,
                "create_time": user_detail.create_time.ToDatetime(
                    tzinfo=pytz.utc
                )
                .astimezone()
                .isoformat(),
                "update_time": user_detail.create_time.ToDatetime(
                    tzinfo=pytz.utc
                )
                .astimezone()
                .isoformat(),
            }
        )


class CallbackPaperFileView(BaseCallbackView):
    logger_name = "callback.paper.file.view"
    paper_service = paper_client.stub

    async def handle(
        self, query: dict[str, str], body: dict[str, str], request: Request
    ) -> JSONResponse:
        paper_id = query.get("paper_id", None)
        if paper_id is None:
            raise ApiException(
                ResponseType.ParamEmpty, "paper_id不能为空", record=True
            )

        key = body.get("object", None)
        if key is None:
            raise ApiException(
                ResponseType.ParamEmpty, "object不能为空", record=True
            )

        self.logger.debug(
            f"callback update paper file, paper_id: {paper_id}, object: {key}"
        )

        paper_detail: PaperDetail = await self.paper_service.UpdateAttachment(
            UpdateAttachmentRequest(
                paper_id=paper_id,
                file=key,
                fetch_metadata=query.get("fetch_metadata", "false").lower()
                == "true",
            )
        )

        result = {
            "id": paper_detail.id,
            "file": paper_detail.file,
        }

        if paper_detail.title != "":
            result["title"] = paper_detail.title
        if paper_detail.abstract != "":
            result["abstract"] = paper_detail.abstract
        if len(list(paper_detail.keywords)) != 0:
            result["keywords"] = list(paper_detail.keywords)
        if len(list(paper_detail.authors)) != 0:
            result["authors"] = list(paper_detail.authors)
        if len(list(paper_detail.tags)) != 0:
            result["tags"] = list(paper_detail.tags)
        if paper_detail.publication_date.ByteSize() != 0:
            result[
                "publication_date"
            ] = f"{paper_detail.publication_date.year}-{paper_detail.publication_date.month}-{paper_detail.publication_date.day}"
        if paper_detail.publication != "":
            result["publication"] = paper_detail.publication
        if paper_detail.issue != "":
            result["issue"] = paper_detail.issue
        if paper_detail.volume != "":
            result["volume"] = paper_detail.volume
        if paper_detail.pages != "":
            result["pages"] = paper_detail.pages
        if paper_detail.doi != "":
            result["doi"] = paper_detail.doi
        if paper_detail.url != "":
            result["url"] = paper_detail.url

        return JSONResponse(result)
