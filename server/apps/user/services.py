from datetime import datetime

from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp
from paperpilot_common.exceptions import ApiException
from paperpilot_common.middleware.server.auth import user_context
from paperpilot_common.protobuf.test.test_pb2 import TestResult
from paperpilot_common.protobuf.user.user_pb2 import UserInfo
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger
from paperpilot_common.utils.types import _ServicerContext
from user.models import User


class UserService:
    logger = get_logger("test.service")

    async def get_user_info(self, user: User | str) -> UserInfo:
        if isinstance(user, str):
            user = await User.objects.filter(id=user).afirst()
            if user is None:
                raise ApiException(
                    ResponseType.ResourceNotFound, msg="用户不存在", record=True
                )

        return UserInfo(
            id=user.id,
            username=user.username,
            avatar=user.avatar.url,
        )


user_service: UserService = UserService()
