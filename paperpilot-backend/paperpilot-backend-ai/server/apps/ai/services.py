from typing import Iterable
from uuid import UUID, uuid4

from paperpilot_common.protobuf.ai.ai_pb2 import FinishReason, GptResult
from paperpilot_common.protobuf.ai.cache_pb2 import Chat, Message, Role
from paperpilot_common.utils.log import get_logger

from server.apps.ai.caches import ai_cache
from server.apps.ai.config import MAX_MESSAGE_LENGTH, MAX_MESSAGES
from server.apps.ai.utils import get_finish_reason_enum
from server.business.gpt.service import GptBusiness


class AiService:
    logger = get_logger("service.ai")
    gpt_service = GptBusiness()
    cache = ai_cache

    prompt = {
        "summarize": "请总结以上内容",
        "rewrite": "请重写以上内容",
        "translate": "请翻译以上内容为中文",
        "explain": "请解释以上内容",
    }

    async def generate_content(
        self, chat_id: UUID | None, text: str, action: str
    ) -> (Chat, FinishReason):
        if text != "":  # 传入论文文本
            action_text = self.prompt.get(action, action)
            content = f"以下是一篇论文的部分内容：\n{text}\n\n{action_text}"
        else:
            content = action

        if len(content) > MAX_MESSAGE_LENGTH:
            return None, FinishReason.MESSAGE_TOO_LONG

        if chat_id is None:  # 新对话
            chat = Chat()
        else:
            chat = await self.cache.get_chat(chat_id)
        if len(chat.messages) // 2 >= MAX_MESSAGES:
            return None, FinishReason.MESSAGE_NUM_LIMIT

        chat.messages.extend(
            [
                Message(
                    role=Role.USER,
                    content=content,
                )
            ],
        )

        return chat, None

    async def ask(
        self, chat_id: UUID | None, text: str, action: str
    ) -> Iterable[GptResult]:
        chat, stop = await self.generate_content(chat_id, text, action)

        if stop:
            yield GptResult(
                content="",
                finish_reason=stop,
            )
            return

        content = [
            {
                "role": "user" if message.role == Role.USER else "assistant",
                "content": message.content,
            }
            for message in chat.messages
        ]

        meta = GptResult(
            total_chat_times=MAX_MESSAGES,
            remain_chat_times=MAX_MESSAGES - (len(chat.messages) + 1) // 2,
        )

        if chat_id is None:
            chat_id = uuid4()
            meta.chat_id = chat_id.hex

        yield meta

        answer_list = []

        async for answer, status in self.gpt_service.ask(content):
            answer_list.append(answer)
            if not status:
                yield GptResult(
                    content=answer,
                )
            else:
                yield GptResult(
                    content=answer,
                    finish_reason=get_finish_reason_enum(status),
                )

        chat.messages.extend(
            [
                Message(
                    role=Role.ASSISTANT,
                    content="".join(answer_list),
                )
            ]
        )

        await self.cache.set_chat(chat_id, chat)


ai_service = AiService()
