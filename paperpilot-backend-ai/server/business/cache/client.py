import redis.asyncio
from paperpilot_common.protobuf.ai.cache_pb2 import Chat, Message, Role

from server.business.cache.config import URL

redis = redis.asyncio.from_url(URL)

if __name__ == "__main__":
    import asyncio

    async def main():
        chat = Chat(
            messages=[
                Message(
                    role=Role.USER,
                    content="Hello",
                ),
                Message(
                    role=Role.ASSISTANT,
                    content="Hi",
                ),
                Message(
                    role=Role.USER,
                    content="How are you?",
                ),
                Message(
                    role=Role.ASSISTANT,
                    content="I'm fine, thank you.",
                ),
            ]
        )

        print(await redis.get("chat"))
        await redis.set("chat", chat.SerializeToString(), ex=10)
        data = await redis.get("chat")
        data = Chat.FromString(data)
        print(
            [
                {
                    "role": "user"
                    if message.role == Role.USER
                    else "assistant",
                    "content": message.content,
                }
                for message in data.messages
            ]
        )
        await redis.delete("chat")
        await redis.aclose()

    asyncio.run(main())
