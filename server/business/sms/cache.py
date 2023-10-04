from paperpilot_common.utils.cache import Cache


class Key:
    """
    缓存键
    """

    @staticmethod
    def phone(phone: str) -> str:
        """
        phone 缓存键
        """
        return f"phone:{phone}"


class SmsCache(Cache):
    """
    Sms 缓存
    """

    logger_name = "business.sms.cache"
    default_timeout = 60

    async def add_phone(self, phone: str):
        """
        添加 phone 缓存
        """
        await self.set_async(
            Key.phone(phone), True, timeout=self.default_timeout
        )

    async def check_phone(self, phone: str) -> bool:
        """
        检查 phone 缓存

        :param phone: 手机号
        :return: 是否存在，False: 手机号未被限流
        """
        return await self.get_async(Key.phone(phone), default=False)


sms_cache: SmsCache = SmsCache()
