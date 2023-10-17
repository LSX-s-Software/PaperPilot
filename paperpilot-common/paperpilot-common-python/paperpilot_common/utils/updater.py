from paperpilot_common.utils.log import get_logger


class Updater:
    fields = []
    logger_name = "updater"

    def __init__(self):
        self.logger = get_logger(self.logger_name)

    async def _update_field(self, field: str, obj, vo) -> None:
        # 寻找diff方法（返回True则进行更新）
        diff_method = getattr(self, f"diff_{field}", None)
        if diff_method:  # 存在自定义diff方法
            if await diff_method(obj, vo) is False:  # diff失败，无需更新
                return
        else:
            if getattr(obj, field) == getattr(vo, field):  # 无需更新
                return

        # 寻找validate方法（校验字段）
        validate_method = getattr(self, f"validate_{field}", None)
        if validate_method:  # 存在自定义validate方法
            await validate_method(obj, vo)

        # 寻找update方法（更新字段）
        update_method = getattr(self, f"update_{field}", None)
        if update_method:  # 存在自定义update方法
            await update_method(obj, vo)
        else:
            setattr(obj, field, getattr(vo, field))

        self.logger.debug(f"update user field success, user: {obj}, field: {field}")

    async def update(self, obj, vo, save=False) -> None:
        """
        更新obj信息

        针对每个field：先diff，再validate，最后update

        :param obj: 对象
        :param vo: 更新vo
        :param save: 是否保存(默认不保存)
        """
        for field in self.fields:  # 遍历待更新字段
            await self._update_field(field, obj, vo)

        if save:
            await obj.asave()
            await obj.arefresh_from_db()

        self.logger.debug(f"update user success, user: {obj}")
