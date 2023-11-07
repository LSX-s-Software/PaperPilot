from typing import Iterable

from paperpilot_common.protobuf.ai.ai_pb2 import GptResult
from paperpilot_common.utils.log import get_logger

from server.apps.ai.utils import get_finish_reason_enum
from server.business.gpt.service import GptBusiness


class AiService:
    logger = get_logger("service.ai")
    gpt_service = GptBusiness()

    prompt = {
        "summarize": "请总结以上内容",
        "rewrite": "请重写以上内容",
        "translate": "请翻译以上内容为中文",
        "explain": "请解释以上内容",
    }

    async def ask(self, text: str, action: str) -> Iterable[GptResult]:
        action_text = self.prompt.get(action, action)
        content = f"以下是一篇论文的部分内容：\n{text}\n\n{action_text}"
        async for answer, status in self.gpt_service.ask(content):
            if not status:
                yield GptResult(
                    content=answer,
                )
            else:
                yield GptResult(
                    content=answer,
                    finish_reason=get_finish_reason_enum(status),
                )


ai_service = AiService()
