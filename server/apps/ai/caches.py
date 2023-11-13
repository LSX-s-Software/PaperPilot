from uuid import UUID

from paperpilot_common.protobuf.ai.cache_pb2 import Chat

from server.business.cache import redis


class CacheKey:
    @staticmethod
    def chat(chat_id: UUID) -> str:
        return f"chat:{chat_id.hex}"


class AiCache:
    client = redis
    ttl = 60 * 60 * 24 * 7  # 7 days

    async def get_chat(self, chat_id: UUID) -> Chat:
        data = await self.client.get(CacheKey.chat(chat_id))
        if data:
            return Chat.FromString(data)
        else:
            return Chat()

    async def set_chat(self, chat_id: UUID, chat: Chat) -> None:
        await self.client.set(
            CacheKey.chat(chat_id), chat.SerializeToString(), ex=self.ttl
        )

    async def delete_chat(self, chat_id: UUID) -> None:
        await self.client.delete(CacheKey.chat(chat_id))


ai_cache: AiCache = AiCache()
