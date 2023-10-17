from oauth.cache import auth_cache
from paperpilot_common.exceptions import ApiException
from paperpilot_common.protobuf.user.user_pb2 import UpdateUserRequest
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.updater import Updater
from user.models import User


class UserUpdater(Updater):
    fields = ["username", "phone", "password"]
    logger_name = "service.user.updater"

    async def diff_password(self, obj: User, vo: UpdateUserRequest) -> bool:
        return vo.new_password is not None

    async def update_password(self, obj: User, vo: UpdateUserRequest) -> None:
        if obj.check_password(vo.old_password) is False:
            raise ApiException(ResponseType.ParamValidationFailed, msg="旧密码错误")
        obj.set_password(vo.new_password)

    async def validate_phone(self, obj: User, vo: UpdateUserRequest) -> None:
        # 验证码校验
        actual_code = await auth_cache.get_code(vo.phone)
        if actual_code is None or actual_code != vo.code:
            self.logger.warning(
                f"register failed, code not match, phone: {vo.phone}"
            )
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="验证码错误，请重试",
                detail="验证码错误",
                record=False,
            )
        await auth_cache.delete_code(vo.phone)
