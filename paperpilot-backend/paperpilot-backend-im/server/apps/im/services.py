from uuid import UUID

from paperpilot_common.protobuf.im.im_pb2 import IMAuthResponse
from paperpilot_common.utils.log import get_logger

from server.apps.im.utils import generate_avatar
from server.business.im import IMApi, auth
from server.utils.truncate import limit_str


class IMService:
    logger = get_logger("apps.im.service")
    auth = auth
    api = IMApi()

    async def get_im_auth(self, user_id: UUID) -> IMAuthResponse:
        sig = self.auth.genUserSig(user_id.hex, expire=3600 * 24)
        return IMAuthResponse(
            id=user_id.hex,
            sig=sig,
        )

    async def create_user(self, user_id: UUID, username: str):
        """
        创建用户

        :param user_id: 用户ID
        :param username: 用户名
        """
        self.logger.info(f"create user {user_id}")
        await self.api.create_user(
            user_id=user_id.hex,
            username=limit_str(username, 32),
            avatar=generate_avatar(username),
        )

    async def update_user(self, user_id: UUID, username: str, avatar: str):
        """
        更新用户

        :param user_id: 用户ID
        :param username: 用户名
        :param avatar: 头像
        """
        self.logger.info(f"update user {user_id}")
        await self.api.update_user(
            user_id=user_id.hex,
            username=limit_str(username, 32),
            avatar=avatar,
        )

    async def create_group(self, group_id: UUID, name: str, owner: str):
        """
        创建群组

        :param group_id: 群组ID
        :param name: 群组名称
        :param owner: 群主
        """
        self.logger.info(f"create group {group_id}")
        await self.api.create_work_group(
            group_id=group_id.hex,
            name=limit_str(name),
            owner=owner,
            avatar=generate_avatar(name),
        )

    async def update_group(self, group_id: UUID, name: str):
        """
        更新群组

        :param group_id: 群组ID
        :param name: 群组名称
        """
        self.logger.info(f"update group {group_id}")
        await self.api.update_work_group(
            group_id=group_id.hex,
            name=limit_str(name),
            avatar=generate_avatar(name),
        )

    async def delete_group(self, group_id: UUID):
        """
        删除群组

        :param group_id: 群组ID
        """
        self.logger.info(f"delete group {group_id}")
        await self.api.delete_work_group(
            group_id=group_id.hex,
        )

    async def add_group_member(self, group_id: UUID, user_id: UUID):
        """
        添加群成员

        :param group_id: 群组ID
        :param user_id: 用户ID
        """
        self.logger.info(f"add group {group_id} member {user_id}")
        await self.api.add_work_group_member(
            group_id=group_id.hex,
            user_id=user_id.hex,
        )

    async def delete_group_member(self, group_id: UUID, user_id: UUID):
        """
        删除群成员

        :param group_id: 群组ID
        :param user_id: 用户ID
        """
        self.logger.info(f"delete group {group_id} member {user_id}")
        await self.api.delete_work_group_member(
            group_id=group_id.hex,
            user_id=user_id.hex,
        )


im_service: IMService = IMService()
