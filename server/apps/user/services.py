import uuid

import oss2
from django.db import IntegrityError
from paperpilot_common.exceptions import ApiException
from paperpilot_common.helper.field import datetime_to_timestamp
from paperpilot_common.oss.backends import OssStorage
from paperpilot_common.protobuf.im.im_pb2 import (
    UpdateUserRequest as IMUpdateUserRequest,
)
from paperpilot_common.protobuf.user.user_pb2 import (
    UpdateUserRequest,
    UserDetail,
    UserInfo,
)
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger
from user.models import User
from user.updaters import UserUpdater
from user.utils import generate_avatar

from server.business.grpc.im import im_client


class UserService:
    logger = get_logger("test.service")
    updater = UserUpdater()

    async def _get_user(self, user: User | uuid.UUID | str) -> User:
        """
        获取用户

        :param user: 用户对象或用户ID
        :return: 用户对象
        """
        if isinstance(user, str):  # 转换为uuid
            user = uuid.UUID(user)

        if isinstance(user, uuid.UUID):  # 转换为用户对象
            user = await User.objects.filter(id=user).afirst()
            if user is None:
                raise ApiException(
                    ResponseType.ResourceNotFound, msg="用户不存在", record=True
                )

        return user

    def _get_user_avatar(self, user: User) -> str:
        """
        获取用户头像

        :param user: 用户对象
        :return: 用户头像地址
        """
        if user.avatar.name == f"{User.AVATAR_PATH}/default.jpg":
            return generate_avatar(user.username)
        if isinstance(user.avatar.storage, OssStorage):
            return user.avatar.file.url(sign=False)
        return user.avatar.url

    async def get_user_info(self, user: User | uuid.UUID | str) -> UserInfo:
        """
        获取用户信息

        :param user: 用户对象或用户ID
        :return: 用户信息
        """
        user = await self._get_user(user)

        self.logger.debug(f"get user info: {user}")
        return UserInfo(
            id=user.id.hex,
            username=user.username,
            avatar=self._get_user_avatar(user),
        )

    async def get_user_detail(self, user: User | uuid.UUID | str) -> UserDetail:
        """
        获取用户详情

        :param user: 用户对象或用户ID
        :return: 用户详情
        """
        user = await self._get_user(user)

        self.logger.debug(f"get user detail: {user}")
        return UserDetail(
            id=user.id.hex,
            username=user.username,
            phone=user.phone,
            avatar=self._get_user_avatar(user),
            create_time=datetime_to_timestamp(user.create_time),
            update_time=datetime_to_timestamp(user.update_time),
        )

    async def update_user(
        self, user_id: uuid.UUID, user_vo: UpdateUserRequest
    ) -> UserDetail:
        """
        更新用户信息

        :param user_id: 用户ID
        :param user_vo: 用户信息
        :return: 用户详情
        """
        user = await self._get_user(user_id)
        try:
            await self.updater.update(user, user_vo, save=True)
        except IntegrityError as e:
            self.logger.warning(f"update user failed, {e}")
            raise ApiException(
                ResponseType.ParamValidationFailed,
                detail="用户名或手机号已存在",
                record=True,
            )

        self.logger.debug(f"update user: {user}")

        # 更新im信息
        await im_client.stub.UpdateUser(
            IMUpdateUserRequest(
                id=user.id.hex,
                username=user.username,
                avatar=self._get_user_avatar(user),
            )
        )

        return await self.get_user_detail(user)

    async def get_user_info_list(
        self, user_ids: list[uuid.UUID]
    ) -> list[UserInfo]:
        """
        获取用户信息列表

        :param user_ids: 用户ID列表
        :return: 用户信息列表
        """
        infos = []
        self.logger.debug(f"get user info list: {user_ids}")

        async for user in User.objects.filter(id__in=user_ids):
            infos.append(
                UserInfo(
                    id=user.id.hex,
                    username=user.username,
                    avatar=self._get_user_avatar(user),
                )
            )

        return infos

    async def update_user_avatar(
        self, user_id: str, avatar_url: str
    ) -> UserDetail:
        """
        更新用户头像

        :param user_id: 用户ID
        :param avatar_url: 头像地址
        :return: None
        """
        user = await self._get_user(user_id)
        user.avatar.name = avatar_url

        if isinstance(user.avatar.storage, OssStorage):  # 切换公共读权限
            user.avatar.file.set_acl(oss2.BUCKET_ACL_PUBLIC_READ)

        await user.asave()
        await user.arefresh_from_db()

        return await self.get_user_detail(user)


user_service: UserService = UserService()
