import oauth.utils as utils
from django.db.models import Q
from paperpilot_common.exceptions import ApiException
from paperpilot_common.protobuf.im.im_pb2 import CreateUserRequest
from paperpilot_common.protobuf.user.auth_pb2 import LoginResponse, Token
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger
from user.models import User
from user.services import user_service

from server.business.grpc.im import im_client
from server.business.jwt import jwt_business
from server.business.sms import sms_business

from .cache import auth_cache

# 登录失败异常
login_failed = ApiException(ResponseType.LoginFailed, msg="用户名或密码错误，请重试")


class AuthService:
    """
    用户认证服务
    """

    logger = get_logger("service.oauth")

    async def _get_access_token(self, user: User) -> Token:
        """
        获取 access token

        :param user: 用户
        """
        token = await jwt_business.generate_access(user.id.hex)
        return token.to_protobuf()

    async def _get_refresh_token(self, user: User) -> Token:
        """
        获取 refresh token

        :param user: 用户
        """
        token = await jwt_business.generate_refresh(user.id.hex)
        return token.to_protobuf()

    async def _generate_login_response(self, user: User) -> LoginResponse:
        return LoginResponse(
            user=await user_service.get_user_info(user),
            access=await self._get_access_token(user),
            refresh=await self._get_refresh_token(user),
        )

    async def login(self, phone: str, password: str) -> LoginResponse:
        """
        登录

        :param phone: 手机号
        :param password: 密码
        :return: 登录响应
        """
        # 尝试根据手机号获取用户
        user = await User.objects.filter(phone=phone).afirst()
        if user is None:  # 用户不存在
            self.logger.warning(
                f"login failed, phone not found, phone: {phone}"
            )
            raise login_failed

        if not user.check_password(password):  # 密码不匹配
            self.logger.warning(
                f"login failed, password not match, phone: {phone}"
            )
            raise login_failed

        self.logger.debug(f"login success, phone: {phone}")

        # 登录成功，更新登录时间
        await user.update_login_time()

        return await self._generate_login_response(user)

    async def refresh(self, refresh: str) -> Token:
        """
        刷新获得 access token

        :param refresh: refresh token
        :return: access token
        """
        # 检查 refresh token 是否存在
        if not await jwt_business.check_refresh(refresh):
            self.logger.debug(
                f"refresh failed, refresh token not found, refresh: {refresh}"
            )
            raise ApiException(
                ResponseType.TokenInvalid,
                detail="refresh token不存在",
                record=False,
            )

        # 解析 refresh token
        payload = await jwt_business.check_refresh(refresh)
        user_id = payload["user_id"]

        # 尝试根据用户 id 获取用户
        user = await User.objects.filter(id=user_id).afirst()
        if user is None:  # 用户不存在
            self.logger.warning(
                f"refresh failed, user not found, user: {user_id}"
            )
            raise ApiException(
                ResponseType.ResourceNotFound, detail="用户不存在", record=True
            )

        self.logger.debug(f"refresh success, user: {user_id}")

        # 刷新成功，更新登录时间
        await user.update_login_time()

        return await self._get_access_token(user)

    async def register(
        self,
        phone: str,
        code: str,
        password: str,
        username: str,
    ) -> LoginResponse:
        """
        注册

        :param phone: 手机号
        :param code: 验证码
        :param password: 密码
        :param username: 用户名
        """
        # 尝试根据手机号或用户名获取用户
        user_count = await User.objects.filter(
            Q(username=username) | Q(phone=phone)
        ).acount()
        if user_count != 0:  # 用户已存在
            self.logger.warning(
                f"register failed, phone already exists, phone: {phone}"
            )
            raise ApiException(
                ResponseType.ParamValidationFailed,
                detail="手机号或用户名已存在",
                record=True,
            )

        # 验证码校验
        actual_code = await auth_cache.get_code(phone)
        if actual_code is None or actual_code != code:
            self.logger.warning(
                f"register failed, code not match, phone: {phone}"
            )
            raise ApiException(
                ResponseType.ParamValidationFailed,
                msg="验证码错误，请重试",
                detail="验证码错误",
                record=False,
            )
        await auth_cache.delete_code(phone)

        # 创建用户
        user = await User.objects.create_user(
            phone=phone,
            password=password,
            username=username,
        )
        self.logger.info(
            f"register success, phone: {phone}, username: {username}"
        )

        # 添加im用户
        await im_client.stub.CreateUser(
            CreateUserRequest(
                id=user.id.hex,
                username=username,
            )
        )

        # 返回token
        return await self._generate_login_response(user)

    async def send_sms_code(self, phone: str) -> None:
        """
        发送短信验证码

        :param phone: 手机号
        """
        code = utils.random_code()

        self.logger.debug(f"send sms code, phone: {phone}, code: {code}")
        await auth_cache.add_code(phone, code)
        await sms_business.send_code(phone, code)

    async def count_phone(self, phone: str) -> int:
        """
        统计手机号数量

        :param phone: 手机号
        :return: 数量
        """
        self.logger.debug(f"count phone, phone: {phone}")
        return await User.objects.filter(phone=phone).acount()

    async def count_username(self, username: str) -> int:
        """
        统计用户名数量

        :param username: 用户名
        :return: 数量
        """
        self.logger.debug(f"count username, username: {username}")
        return await User.objects.filter(username=username).acount()


auth_service: AuthService = AuthService()
