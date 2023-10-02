from paperpilot_common.utils.cache import Cache

from .config import access_lifetime, refresh_lifetime


class Key:
    """
    缓存键
    """

    @staticmethod
    def access(token: str) -> str:
        """
        access token 缓存键
        """
        return f"access:{token}"

    @staticmethod
    def refresh(token: str) -> str:
        """
        refresh token 缓存键
        """
        return f"refresh:{token}"


class JwtCache(Cache):
    """
    JWT 缓存
    """

    logger_name = "business.jwt.cache"

    async def add_access(self, token: str) -> None:
        """
        添加 access token

        :param token: access token
        """
        await self.set_async(
            Key.access(token),
            True,
            timeout=int(access_lifetime.total_seconds()),
        )

    async def add_refresh(self, token: str) -> None:
        """
        添加 refresh token

        :param token: refresh token
        """
        await self.set_async(
            Key.refresh(token),
            True,
            timeout=int(refresh_lifetime.total_seconds()),
        )

    async def check_access(self, token: str) -> bool:
        """
        检查 access token 是否存在

        :param token: access token
        :return: 是否存在
        """
        return await self.get_async(Key.access(token), False)

    async def check_refresh(self, token: str) -> bool:
        """
        检查 refresh token 是否存在

        :param token: refresh token
        :return: 是否存在
        """
        return await self.get_async(Key.refresh(token), False)

    async def delete_access(self, token: str) -> None:
        """
        删除 access token

        :param token: access token
        """
        await self.delete_async(Key.access(token))

    async def delete_refresh(self, token: str) -> None:
        """
        删除 refresh token

        :param token: refresh token
        """
        await self.delete_async(Key.refresh(token))


jwt_cache: JwtCache = JwtCache()
