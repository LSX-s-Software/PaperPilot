from paperpilot_common.utils.cache import Cache


class Key:
    @staticmethod
    def code(phone: str) -> str:
        return f"code:{phone}"


class AuthCache(Cache):
    """
    认证 缓存
    """

    logger_name = "oauth.cache"
    default_timeout = 300

    async def add_code(self, phone: str, code: str) -> None:
        """
        添加 code

        :param phone: 手机号
        :param code: 验证码
        """
        await self.set_async(
            Key.code(phone), code, timeout=self.default_timeout
        )

    async def get_code(self, phone: str) -> str | None:
        """
        获取 code

        :param phone: 手机号
        :return: 验证码
        """
        return await self.get_async(Key.code(phone), None)

    async def delete_code(self, phone: str) -> None:
        """
        删除 code

        :param phone: 手机号
        """
        await self.delete_async(Key.code(phone))


auth_cache: AuthCache = AuthCache()
