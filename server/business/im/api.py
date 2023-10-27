import datetime
import random
import urllib.parse

import aiohttp
from paperpilot_common.exceptions import ApiException
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger

from server.business.im.auth import auth


class IMApi:
    endpoint = "console.tim.qq.com"

    logger = get_logger("business.im.api")

    def __init__(self):
        from server.business.im.config import admin, app_id

        self.app_id = app_id
        self.admin = admin

        self.admin_sig = None
        self.admin_sig_expire = datetime.datetime.now()

        self.client = aiohttp.ClientSession()

    def _refresh_admin_sig(self):
        """
        刷新管理员签名
        """
        if (
            self.admin_sig_expire > datetime.datetime.now()
            and self.admin_sig is not None
        ):
            return

        expire = datetime.timedelta(days=30)

        self.admin_sig = auth.genUserSig(
            self.admin, expire=int(expire.total_seconds()) + 60
        )
        self.admin_sig_expire = datetime.datetime.now() + expire
        self.logger.info(f"refresh admin sig, expire: {self.admin_sig_expire}")

    # def _save_example_response(self, api: str, response: dict):
    #     import pathlib
    #     import json
    #
    #     ROOT = pathlib.Path(__file__).parent.parent.parent.parent
    #     RESOURCE = ROOT / "tests" / "resource"
    #
    #     path_list = api.strip("/").split("/")
    #     path = RESOURCE / "/".join(path_list[:-1])
    #     file = path / f"{path_list[-1]}.json"
    #
    #     if not path.exists():
    #         path.mkdir(parents=True)
    #
    #     with open(file, "w", encoding="utf-8") as f:
    #         f.write(json.dumps(response, indent=4))

    async def _request(self, api: str, data: dict = None) -> dict:
        """
        发起请求

        :param api: 请求API地址
        :param data: 请求数据
        """
        self._refresh_admin_sig()

        if data is None:
            data = {}

        query = {
            "sdkappid": self.app_id,
            "identifier": self.admin,
            "usersig": self.admin_sig,
            "random": random.randint(0, 4294967295),
            "contenttype": "json",
        }

        url = f"https://{self.endpoint}{api}?{urllib.parse.urlencode(query)}"

        async with self.client.post(url, json=data) as resp:
            result = await resp.json()

            self.logger.debug(
                f"request im api, url: {url}, data: {data}, result: {result}"
            )

            if result["ErrorCode"] != 0:
                raise ApiException(
                    ResponseType.ThirdServiceError,
                    msg=result["ErrorInfo"],
                )

            return result

    async def create_user(
        self, user_id: str, username: str, avatar: str
    ) -> dict:
        """
        创建用户

        :param user_id: 用户ID
        :param username: 用户名
        :param avatar: 头像url
        """
        return await self._request(
            "/v4/im_open_login_svc/account_import",
            {
                "UserID": user_id,
                "Nick": username,
                "FaceUrl": avatar,
            },
        )

    async def update_user(self, user_id: str, username: str, avatar: str):
        """
        更新用户

        :param user_id: 用户ID
        :param username: 用户名
        :param avatar: 头像url
        """
        return await self._request(
            "/v4/profile/portrait_set",
            {
                "From_Account": user_id,
                "ProfileItem": [
                    {
                        "Tag": "Tag_Profile_IM_Nick",
                        "Value": username,
                    },
                    {
                        "Tag": "Tag_Profile_IM_Image",
                        "Value": avatar,
                    },
                ],
            },
        )

    async def create_work_group(
        self, owner: str, name: str, avatar: str, group_id: str
    ):
        """
        创建Work群

        :param owner: 群主ID
        :param name: 群名称
        :param avatar: 群头像
        :param group_id: 群ID
        """
        return await self._request(
            "/v4/group_open_http_svc/create_group",
            {
                "Owner_Account": owner,
                "Type": "Work",
                "Name": name,
                "GroupId": group_id,
                "FaceUrl": avatar,
                "InviteJoinOption": "DisableInvite",
            },
        )

    async def update_work_group(self, group_id: str, name: str, avatar: str):
        """
        更新Work群

        :param group_id: 群ID
        :param name: 群名称
        :param avatar: 群头像
        """
        return await self._request(
            "/v4/group_open_http_svc/modify_group_base_info",
            {
                "GroupId": group_id,
                "Name": name,
                "FaceUrl": avatar,
            },
        )

    async def delete_work_group(self, group_id: str):
        """
        删除Work群

        :param group_id: 群ID
        """
        return await self._request(
            "/v4/group_open_http_svc/destroy_group",
            {
                "GroupId": group_id,
            },
        )

    async def add_work_group_member(self, group_id: str, user_id: str):
        """
        邀请Work群成员

        :param group_id: 群ID
        :param user_id: 用户ID
        """
        return await self._request(
            "/v4/group_open_http_svc/add_group_member",
            {
                "GroupId": group_id,
                "MemberList": [
                    {
                        "Member_Account": user_id,
                    },
                ],
            },
        )

    async def delete_work_group_member(self, group_id: str, user_id: str):
        """
        删除Work群成员

        :param group_id: 群ID
        :param user_id: 用户ID
        """
        return await self._request(
            "/v4/group_open_http_svc/delete_group_member",
            {
                "GroupId": group_id,
                "MemberToDel_Account": [
                    user_id,
                ],
            },
        )
