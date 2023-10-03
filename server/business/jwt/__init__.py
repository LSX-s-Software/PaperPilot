import datetime

import jwt
from google.protobuf.timestamp_pb2 import Timestamp
from paperpilot_common.exceptions import ApiException
from paperpilot_common.protobuf.user.auth_pb2 import Token as TokenPb
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger

from .cache import jwt_cache
from .config import access_lifetime, algorithm, refresh_lifetime, secret


class Token:
    """
    Token 数据类型
    """

    value: str  # token 值
    expire_time: int  # 过期时间

    def __init__(self, value: str, expire_time: int):
        self.value = value
        self.expire_time = expire_time

    def to_protobuf(self) -> TokenPb:
        """
        转换为 protobuf 类型
        """
        t = Timestamp()
        t.FromSeconds(self.expire_time)
        return TokenPb(
            value=self.value,
            expire_time=t,
        )


class JwtBusiness:
    """
    JWT 业务
    """

    logger = get_logger("business.jwt")

    ACCESS_ISS = "kong"  # access token 签发者
    REFRESH_ISS = "paperpilot"  # refresh token 签发者
    ACCESS_AUD = "kong"  # access token 接收者
    REFRESH_AUD = "paperpilot"  # refresh token 接收者

    TYPE_ACCESS = "access"  # access token 类型
    TYPE_REFRESH = "refresh"  # refresh token 类型

    async def generate_access(self, user_id: str) -> Token:
        """
        生成 access token

        :param user_id: 用户 id
        :return: access token
        """
        self.logger.debug(f"generate access token for user: {user_id}")
        payload = {
            "user_id": user_id,  # 用户 id
            "exp": int(
                (datetime.datetime.utcnow() + access_lifetime).timestamp()
            ),  # 过期时间
            "iat": int(datetime.datetime.utcnow().timestamp()),  # 签发时间
            "iss": self.ACCESS_ISS,  # 签发者
            "type": self.TYPE_ACCESS,  # token 类型
            "aud": self.ACCESS_AUD,  # 接收者
        }
        token = jwt.encode(payload, secret, algorithm=algorithm)
        await jwt_cache.add_access(token)  # 缓存 access token，用于校验
        return Token(value=token, expire_time=payload["exp"])

    async def generate_refresh(self, user_id: str) -> Token:
        """
        生成 refresh token

        :param user_id: 用户 id
        :return: refresh token
        """
        self.logger.debug(f"generate refresh token for user: {user_id}")
        payload = {
            "user_id": user_id,
            "exp": int(
                (datetime.datetime.utcnow() + refresh_lifetime).timestamp()
            ),
            "iat": int(datetime.datetime.utcnow().timestamp()),
            "iss": self.REFRESH_ISS,
            "type": self.TYPE_REFRESH,
            "aud": self.REFRESH_AUD,
        }
        token = jwt.encode(payload, secret, algorithm=algorithm)
        await jwt_cache.add_refresh(token)
        return Token(value=token, expire_time=payload["exp"])

    async def check_access(self, token: str) -> dict:
        """
        检查 access token 合法性

        :param token: access token
        :return: 用户 id
        """
        if not await jwt_cache.check_access(token):
            self.logger.debug(
                f"access token not found in cache, token: {token}"
            )
            raise ApiException(
                ResponseType.TokenInvalid, detail="access token无效", record=False
            )

        try:
            payload = jwt.decode(
                jwt=token,
                key=secret,
                algorithms=[algorithm],
                issuer=self.ACCESS_ISS,
                audience=self.ACCESS_AUD,
                options={
                    "require": ["user_id", "exp", "iat", "iss", "type", "aud"],
                    "verify_signature": True,
                    "verify_iat": True,
                    "verify_exp": True,
                    "verify_nbf": False,
                    "verify_iss": True,
                    "strict_aud": True,
                },
            )
        except jwt.ExpiredSignatureError as e:
            self.logger.debug(
                f"access token invalid, token: {token}, error: {e}"
            )
            raise ApiException(
                ResponseType.TokenExpired,
                detail="access token过期",
                inner=e,
                record=False,
            )
        except jwt.DecodeError as e:
            self.logger.debug(
                f"access token decode failed, token: {token}, error: {e}"
            )
            raise ApiException(
                ResponseType.TokenInvalid,
                detail="access token解析失败",
                inner=e,
                record=True,
            )

        if payload["type"] != self.TYPE_ACCESS:
            self.logger.debug(f"invalid token type, token: {token}")
            raise ApiException(
                ResponseType.TokenInvalid, detail="token类型错误", record=True
            )

        return {
            "user_id": payload["user_id"],
        }

    async def check_refresh(self, token: str) -> dict:
        """
        检查 refresh token 合法性

        :param token: refresh token
        :return: 自定义 paylod
        """
        if not await jwt_cache.check_refresh(token):
            self.logger.debug(
                f"refresh token not found in cache, token: {token}"
            )
            raise ApiException(
                ResponseType.RefreshTokenExpired,
                detail="refresh token无效",
                record=False,
            )

        try:
            payload = jwt.decode(
                jwt=token,
                key=secret,
                algorithms=[algorithm],
                issuer=self.REFRESH_ISS,
                audience=self.REFRESH_AUD,
                options={
                    "require": ["user_id", "exp", "iat", "iss", "type", "aud"],
                    "verify_signature": True,
                    "verify_iat": True,
                    "verify_exp": True,
                    "verify_nbf": False,
                    "verify_iss": True,
                    "strict_aud": True,
                },
            )
        except jwt.ExpiredSignatureError as e:
            self.logger.debug(
                f"refresh token invalid, token: {token}, error: {e}"
            )
            raise ApiException(
                ResponseType.RefreshTokenExpired,
                detail="refresh token过期",
                inner=e,
                record=False,
            )
        except jwt.DecodeError as e:
            self.logger.debug(
                f"refresh token decode failed, token: {token}, error: {e}"
            )
            raise ApiException(
                ResponseType.RefreshTokenInvalid,
                detail="refresh token解析失败",
                inner=e,
                record=True,
            )

        if payload["type"] != self.TYPE_REFRESH:
            self.logger.debug(f"invalid token type, token: {token}")
            raise ApiException(
                ResponseType.RefreshTokenInvalid,
                detail="token类型错误",
                record=True,
            )

        return {
            "user_id": payload["user_id"],
        }


jwt_business = JwtBusiness()

__all__ = ["jwt_business"]
