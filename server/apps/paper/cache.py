from paperpilot_common.utils.cache import Cache


class Key:
    @staticmethod
    def user_project(user: str, project: str) -> str:
        return f"user_project:{user}:{project}"


class ProjectCache(Cache):
    """
    项目 缓存
    """

    logger_name = "project.cache"
    default_timeout = 5

    async def add_user_project(
        self, user: str, project: str, value: bool
    ) -> None:
        """
        添加 user_project

        :param user: 用户
        :param project: 项目
        :param value: 值
        """
        await self.set_async(
            Key.user_project(user, project),
            value,
            timeout=self.default_timeout,
        )

    async def get_user_project(self, user: str, project: str) -> bool | None:
        """
        获取 user_project

        :param user: 用户
        :param project: 项目
        :return: 值
        """
        return await self.get_async(Key.user_project(user, project), None)


project_cache: ProjectCache = ProjectCache()
