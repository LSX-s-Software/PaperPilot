import uuid

from paper.models import Paper
from paperpilot_common.exceptions import ApiException
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger


class PaperService:
    logger = get_logger("paper.service")

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


paper_service: PaperService = PaperService()
