import uuid

from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from paper.models import Paper
from paperpilot_common.exceptions import ApiException
from paperpilot_common.helper.field import datetime_to_timestamp
from paperpilot_common.oss.utils import get_random_name
from paperpilot_common.protobuf.paper.paper_pb2 import PaperDetail
from paperpilot_common.protobuf.project.project_pb2 import (
    CheckUserJoinedProjectRequest,
)
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger

from server.business.grpc.project import project_client
from server.business.research import CrossRefMetaFetch, ScihubFetch

from .cache import project_cache
from .updaters import PaperPublicUpdater, PaperUpdater


class PaperService:
    logger = get_logger("paper.service")
    project = project_client

    paper_updater = PaperUpdater()
    paper_public_updater = PaperPublicUpdater()

    pdf_fetch = ScihubFetch()
    meta_fetch = CrossRefMetaFetch()

    async def _check_user_project(
        self, user_id: uuid.UUID, project_id: uuid.UUID
    ):
        """
        检查用户是否有权限操作项目

        :param user_id: 用户ID
        :param project_id: 项目ID
        :return: None
        :raise: ApiException 无权限
        """
        result = await project_cache.get_user_project(
            user=user_id.hex, project=project_id.hex
        )

        if result is None:  # 缓存中不存在
            # 调用grpc接口获取
            result = await self.project.stub.CheckUserJoinedProject(
                CheckUserJoinedProjectRequest(
                    user_id=user_id.hex, project_id=project_id.hex
                )
            )
            result = result.value
            # 写入缓存
            await project_cache.add_user_project(
                user=user_id.hex, project=project_id.hex, value=result
            )

        if not result:  # 无权限
            raise ApiException(
                ResponseType.PermissionDenied, msg="无权限访问该项目内容", record=True
            )

    async def check_paper_permission(
        self, user_id: uuid.UUID, paper_id: uuid.UUID
    ) -> None:
        """
        检查用户是否有权限操作论文

        :param user_id: 用户ID
        :param paper_id: 论文ID
        :return: None
        """
        paper = await self._get_paper(paper_id)

        await self._check_user_project(user_id, paper.project_id)

    async def _get_paper(self, paper: Paper | uuid.UUID | str) -> Paper:
        """
        获取论文对象

        :param paper: 论文对象或论文ID
        :return: 论文对象
        """
        if isinstance(paper, str):  # 转换为uuid
            paper = uuid.UUID(paper)

        if isinstance(paper, uuid.UUID):  # 转换为论文对象
            paper = await Paper.objects.filter(id=paper).afirst()
            if paper is None:
                raise ApiException(
                    ResponseType.ResourceNotFound, msg="论文不存在", record=True
                )

        return paper

    async def _get_paper_detail(self, paper: Paper) -> PaperDetail:
        """
        获取论文详情

        :param paper: 论文对象
        :return: 论文详情
        """

        detail = PaperDetail(
            id=paper.id.hex,
            project_id=paper.project_id.hex,
            title=paper.title,
            abstract=paper.abstract,
            publication_year=paper.publication_year,
            publication=paper.publication,
            event=paper.event,
            volume=paper.volume,
            issue=paper.issue,
            pages=paper.pages,
            doi=paper.doi,
            url=paper.url,
            file=paper.file.url if paper.file else "",
            create_time=datetime_to_timestamp(paper.create_time),
            update_time=datetime_to_timestamp(paper.update_time),
        )

        detail.authors.extend(paper.authors)
        detail.keywords.extend(paper.keywords)
        detail.tags.extend(paper.tags)

        return detail

    async def get_paper_list(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        page: int,
        page_size: int,
        order_by: str,
    ) -> (list[PaperDetail], int, int):
        """
        获取论文列表

        :param user_id: 用户ID
        :param project_id: 项目ID
        :param page: 页码
        :param page_size: 页大小
        :param order_by: 排序
        :return: 论文列表，总数，下一页
        """

        await self._check_user_project(user_id, project_id)

        queryset = Paper.objects.filter(project_id=project_id)

        total = await queryset.acount()

        if total == 0:  # 无论文
            return [], 0, 0

        # 计算下一页
        next_page = page + 1 if page * page_size < total else 0

        # 排序
        queryset = queryset.order_by(order_by)

        # 分页
        queryset = queryset[(page - 1) * page_size : page * page_size]

        papers = []

        async for paper in queryset.all():
            papers.append(await self._get_paper_detail(paper))

        return papers, total, next_page

    async def get_paper(
        self, user_id: uuid.UUID, paper_id: uuid.UUID
    ) -> PaperDetail:
        """
        获取论文详情

        :param user_id: 用户ID
        :param paper_id: 论文ID
        :return: 论文详情
        """
        paper = await self._get_paper(paper_id)

        await self._check_user_project(user_id, paper.project_id)

        return await self._get_paper_detail(paper)

    async def create_paper_user(
        self, user_id: uuid.UUID, project_id: uuid.UUID, vo: PaperDetail
    ) -> PaperDetail:
        """
        创建论文(用户)

        :param user_id: 用户ID
        :param project_id: 项目ID
        :param vo: 论文详情
        :return: 论文详情
        """
        await self._check_user_project(user_id, project_id)

        paper = Paper()

        await self.paper_public_updater.update(paper, vo)
        paper.project_id = project_id
        await paper.asave()

        return await self._get_paper_detail(paper)

    async def update_paper_user(
        self, user_id: uuid.UUID, paper_id: uuid.UUID, vo: PaperDetail
    ) -> PaperDetail:
        """
        更新论文

        :param user_id: 用户ID
        :param paper_id: 论文ID
        :param vo: 论文详情
        """
        paper = await self._get_paper(paper_id)

        await self._check_user_project(user_id, paper.project_id)

        await self.paper_public_updater.update(paper, vo, save=True)

        return await self._get_paper_detail(paper)

    async def delete_paper(
        self, user_id: uuid.UUID, paper_id: uuid.UUID
    ) -> None:
        """
        删除论文

        :param user_id: 用户ID
        :param paper_id: 论文ID
        :return: None
        """
        paper = await self._get_paper(paper_id)

        await self._check_user_project(user_id, paper.project_id)

        await paper.adelete()

    async def create_paper(self, vo: PaperDetail) -> PaperDetail:
        """
        创建论文

        :param vo: 论文详情
        :return: 论文详情
        """
        paper = Paper()

        await self.paper_updater.update(paper, vo)
        await paper.asave()

        return await self._get_paper_detail(paper)

    async def update_paper(
        self, paper_id: uuid.UUID, vo: PaperDetail
    ) -> PaperDetail:
        """
        更新论文

        :param paper_id: 论文ID
        :param vo: 论文详情
        """
        paper = await self._get_paper(paper_id)

        await self.paper_updater.update(paper, vo, save=True)

        return await self._get_paper_detail(paper)

    async def create_paper_by_link(
        self, user_id: uuid.UUID, project_id: uuid.UUID, url: str
    ) -> PaperDetail:
        """
        通过链接创建论文

        :param user_id: 用户ID
        :param project_id: 项目ID
        :param url: 链接
        """
        await self._check_user_project(user_id, project_id)

        pdf_file = await self.pdf_fetch.fetch(url)

        if not pdf_file.success:
            raise ApiException(
                ResponseType.ThirdServiceError,
                msg="获取PDF文件失败",
                detail="很抱歉，您输入的链接暂不支持直接创建论文，请尝试其他方法创建",
                record=False,
            )

        paper = Paper()

        paper.url = url

        metadata = pdf_file.metadata

        if "author" in metadata:
            paper.authors = metadata["author"]
        if "year" in metadata:
            paper.publication_year = int(metadata["year"])
        if "title" in metadata:
            paper.title = metadata["title"]
        if "publication" in metadata:
            paper.publication = metadata["publication"]
        if "doi" in metadata:
            paper.doi = metadata["doi"]

        paper.project_id = project_id

        metadata = await self.meta_fetch.fetch(paper.doi)

        if metadata.title:
            paper.title = metadata.title
        if metadata.authors:
            paper.authors = metadata.authors
        if metadata.publication:
            paper.publication = metadata.publication
        if metadata.publication_year:
            paper.publication_year = metadata.publication_year
        if metadata.event:
            paper.event = metadata.event

        await self._upload_file(paper, pdf_file.file)

        await paper.asave()

        return await self._get_paper_detail(paper)

    @sync_to_async
    def _upload_file(self, paper: Paper, file: bytes):
        filename = get_random_name(".pdf")
        paper.file.save(filename, ContentFile(file, name=filename))

    async def update_attachment(
        self, paper_id: uuid.UUID, file: str, fetch_metadata: bool
    ) -> PaperDetail:
        """
        更新论文附件

        :param paper_id: 论文ID
        :param file: 文件
        :param fetch_metadata: 是否获取元数据
        :return: 获取的论文数据
        """
        paper = await self._get_paper(paper_id)

        paper.file.name = file

        await paper.asave()

        paper_detail = PaperDetail(id=paper.id.hex, file=paper.file.url)

        if fetch_metadata:
            pass

        return paper_detail


paper_service: PaperService = PaperService()
