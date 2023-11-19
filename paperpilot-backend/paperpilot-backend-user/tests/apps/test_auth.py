import pytest
from django.utils import timezone
from google.protobuf.empty_pb2 import Empty
from oauth.cache import auth_cache
from oauth.urls import AuthPublicController
from paperpilot_common.exceptions import ApiException
from paperpilot_common.protobuf.user.auth_pb2 import (
    CountPhoneRequest,
    CountUsernameRequest,
    LoginRequest,
    RefreshTokenRequest,
    SendSmsCodeRequest,
)
from paperpilot_common.protobuf.user.user_pb2 import CreateUserRequest
from paperpilot_common.response import ResponseType
from pytz import utc
from user.models import User
from user.services import user_service

from server.business.jwt import jwt_business, jwt_cache


class TestAuth:
    @pytest.fixture
    def api(self):
        return AuthPublicController()

    @pytest.mark.asyncio
    async def test_login__success(
        self, api, context, user: User, password, phone
    ):
        request = LoginRequest(phone=phone, password=password)

        response = await api.Login(request, context)

        assert response.user == await user_service.get_user_info(user)

        assert (
            response.access.expire_time.ToDatetime(tzinfo=utc) > timezone.now()
        )
        assert (await jwt_business.check_access(response.access.value))[
            "user_id"
        ] == user.id.hex

        assert (
            response.refresh.expire_time.ToDatetime(tzinfo=utc) > timezone.now()
        )
        assert (await jwt_business.check_refresh(response.refresh.value))[
            "user_id"
        ] == user.id.hex

    @pytest.mark.asyncio
    async def test_login__wrong(self, db, api, context, password, phone):
        request = LoginRequest(phone=phone, password=password)

        with pytest.raises(ApiException) as exc:
            await api.Login(request, context)

        assert exc.value.response_type == ResponseType.LoginFailed

    @pytest.mark.asyncio
    async def test_count_phone(self, api, context, user: User, password, phone):
        result = await api.CountPhone(CountPhoneRequest(phone=phone), context)
        assert result.count == 1

        result = await api.CountPhone(CountPhoneRequest(phone="0"), context)
        assert result.count == 0

    @pytest.mark.asyncio
    async def test_count_username(
        self, api, context, user: User, password, phone
    ):
        result = await api.CountUsername(
            CountUsernameRequest(username=user.username), context
        )
        assert result.count == 1

        result = await api.CountUsername(
            CountUsernameRequest(username="0"), context
        )
        assert result.count == 0

    @pytest.mark.asyncio
    async def test_register__success(
        self, api, context, db, password, phone, code
    ):
        await auth_cache.add_code(phone, code)

        request = CreateUserRequest(
            username="test",
            password=password,
            phone=phone,
            code=code,
        )

        response = await api.Register(request, context)

        user = await User.objects.filter(phone=phone).afirst()

        assert user.check_password(password)

        assert response.user == await user_service.get_user_info(user)

        assert (
            response.access.expire_time.ToDatetime(tzinfo=utc) > timezone.now()
        )
        assert (await jwt_business.check_access(response.access.value))[
            "user_id"
        ] == user.id.hex

        assert (
            response.refresh.expire_time.ToDatetime(tzinfo=utc) > timezone.now()
        )
        assert (await jwt_business.check_refresh(response.refresh.value))[
            "user_id"
        ] == user.id.hex

    @pytest.mark.asyncio
    async def test_register__wrong_code(
        self, api, context, db, password, phone, code
    ):
        request = CreateUserRequest(
            username="test",
            password=password,
            phone=phone,
            code=code,
        )

        with pytest.raises(ApiException) as exc:
            await api.Register(request, context)

        assert exc.value.response_type == ResponseType.ParamValidationFailed

    @pytest.mark.asyncio
    async def test_register__wrong_phone_username(
        self, api, context, user, username, password, phone, code
    ):
        await auth_cache.add_code(phone, code)

        request = CreateUserRequest(
            username=username,
            password=password,
            phone=phone,
            code=code,
        )

        with pytest.raises(ApiException) as exc:
            await api.Register(request, context)

        assert exc.value.response_type == ResponseType.ParamValidationFailed

    @pytest.mark.asyncio
    async def test_refresh__success(self, api, context, user: User):
        refresh_token = await jwt_business.generate_refresh(user.id.hex)

        request = RefreshTokenRequest(refresh=refresh_token.value)

        response = await api.Refresh(request, context)

        assert (
            response.access.expire_time.ToDatetime(tzinfo=utc) > timezone.now()
        )
        assert (await jwt_business.check_access(response.access.value))[
            "user_id"
        ] == user.id.hex

    @pytest.mark.asyncio
    async def test_refresh__wrong(self, api, context, user: User):
        await jwt_cache.add_refresh("0")  # set a wrong refresh token to cache
        request = RefreshTokenRequest(refresh="0")

        with pytest.raises(ApiException) as exc:
            await api.Refresh(request, context)

        assert exc.value.response_type == ResponseType.RefreshTokenInvalid

    @pytest.mark.asyncio
    async def test_send_sms_code__success(self, api, context, phone, code):
        request = SendSmsCodeRequest(phone=phone)

        result = await api.SendSmsCode(request, context)

        assert result == Empty()

        assert await auth_cache.get_code(phone) == code
