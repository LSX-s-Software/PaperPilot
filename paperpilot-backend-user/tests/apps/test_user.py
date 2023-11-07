import random
import uuid

import pytest
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from google.protobuf.empty_pb2 import Empty
from oauth.cache import auth_cache
from paperpilot_common.exceptions import ApiException
from paperpilot_common.helper.field import datetime_to_timestamp
from paperpilot_common.protobuf.user.user_pb2 import (
    UpdateUserAvatarRequest,
    UpdateUserRequest,
    UserId,
    UserIdList,
)
from paperpilot_common.response import ResponseType
from user.models import User
from user.services import user_service
from user.urls import UserController, UserPublicController
from user.utils import generate_avatar


class TestUserPublic:
    @pytest.fixture
    def api(self):
        return UserPublicController()

    @pytest.mark.asyncio
    async def test_get_user_info(self, api, context, user: User):
        response = await api.GetUserInfo(UserId(id=user.id.hex), context)

        assert response.id == user.id.hex
        assert response.username == user.username
        assert response.avatar == generate_avatar(user.username)

    @pytest.mark.asyncio
    async def test_get_current_user__success(self, api, context, user: User):
        context.authenticate(user.id)
        response = await api.GetCurrentUser(Empty(), context)

        assert response.id == user.id.hex
        assert response.username == user.username
        assert response.avatar == generate_avatar(user.username)
        assert response.phone == user.phone
        assert response.create_time == datetime_to_timestamp(user.create_time)
        assert response.update_time == datetime_to_timestamp(user.update_time)

    @pytest.mark.asyncio
    async def test_get_current_user__not_login(self, api, context):
        with pytest.raises(AttributeError):
            await api.GetCurrentUser(Empty(), context)

    @pytest.mark.asyncio
    async def test_update_user__success(
        self, api, context, user: User, password, code
    ):
        context.authenticate(user.id)
        request = UpdateUserRequest(
            username="test-username-2",
            old_password=password,
            new_password="test-password-2",
            phone="13012341234",
            code=code,
        )
        await auth_cache.add_code("13012341234", code)
        response = await api.UpdateUser(request, context)

        user = await User.objects.filter(id=user.id).afirst()

        assert user.username == request.username
        assert user.check_password(request.new_password)
        assert user.phone == request.phone

        assert response == await user_service.get_user_detail(user.id)

    @pytest.mark.asyncio
    async def test_update_user__same_field(
        self, api, context, user: User, password, code
    ):
        context.authenticate(user.id)
        request = UpdateUserRequest(
            username=user.username,
            # old_password=password,
            # new_password=password,
            phone=user.phone,
        )
        await auth_cache.add_code(user.phone, code)
        await api.UpdateUser(request, context)

        user = await User.objects.filter(id=user.id).afirst()

        assert user.username == request.username
        assert user.check_password(password)
        assert user.phone == request.phone

    @pytest.mark.asyncio
    async def test_update_user__wrong_password(
        self, api, context, user: User, password, code
    ):
        context.authenticate(user.id)
        request = UpdateUserRequest(
            username="test-username-2",
            old_password="wrong-password",
            new_password="test-password-2",
            phone="13012341234",
            code=code,
        )
        await auth_cache.add_code("13012341234", code)

        with pytest.raises(ApiException) as e:
            await api.UpdateUser(request, context)

        assert e.value.response_type == ResponseType.ParamValidationFailed

    @pytest.mark.asyncio
    async def test_update_user__wrong_code(
        self, api, context, user: User, password, code
    ):
        context.authenticate(user.id)
        request = UpdateUserRequest(
            username="test-username-2",
            old_password=password,
            new_password="test-password-2",
            phone="13012341234",
            code=code,
        )
        await auth_cache.add_code("13012341234", "wrong-code")

        with pytest.raises(ApiException) as e:
            await api.UpdateUser(request, context)

        assert e.value.response_type == ResponseType.ParamValidationFailed

    @pytest.mark.asyncio
    async def test_update_user__conflict_phone(
        self, api, context, user: User, password, code
    ):
        await User.objects.create_user(
            username="test-username-3",
            password="test-password-2",
            phone="13012340000",
        )

        assert await User.objects.filter(phone="13012340000").acount() == 1

        context.authenticate(user.id)
        request = UpdateUserRequest(
            phone="13012340000",
            code=code,
        )
        await auth_cache.add_code("13012340000", code)

        with pytest.raises(ApiException) as e:
            await api.UpdateUser(request, context)

        assert e.value.response_type == ResponseType.ParamValidationFailed

        await User.objects.filter(phone="13012340000").adelete()

    @pytest.mark.asyncio
    async def test_update_user__conflict_username(
        self, api, context, user: User, password, code
    ):
        await User.objects.create_user(
            username="test-username-3",
            password="test-password-2",
            phone="13012340000",
        )

        assert (
            await User.objects.filter(username="test-username-3").acount() == 1
        )

        context.authenticate(user.id)
        request = UpdateUserRequest(
            username="test-username-3",
        )

        with pytest.raises(ApiException) as e:
            await api.UpdateUser(request, context)

        assert e.value.response_type == ResponseType.ParamValidationFailed

        await User.objects.filter(username="test-username-3").adelete()

    @pytest.mark.asyncio
    async def test_update_user__not_login(
        self, api, context, user: User, password, code
    ):
        request = UpdateUserRequest(
            username="test-username-2",
            old_password=password,
            new_password="test-password-2",
            phone="13012341234",
            code=code,
        )
        await auth_cache.add_code("13012341234", code)

        with pytest.raises(AttributeError):
            await api.UpdateUser(request, context)

    @pytest.mark.asyncio
    async def test_upload_avatar__success(self, api, context, user: User):
        context.authenticate(user.id)
        request = Empty()
        response = await api.UploadUserAvatar(request, context)

        assert response.token is not None
        from django.conf import settings

        assert (
            response.token.access_key_id == settings.ALIYUN_OSS["ACCESS_KEY_ID"]
        )

    @pytest.mark.asyncio
    async def test_upload_avatar__not_login(self, api, context):
        request = Empty()

        with pytest.raises(AttributeError):
            await api.UploadUserAvatar(request, context)


class TestUser:
    @pytest.fixture
    def api(self):
        return UserController()

    @pytest.mark.asyncio
    async def test_get_user_info__success(self, api, context, user: User):
        response = await api.GetUserInfo(UserId(id=user.id.hex), context)

        assert response.id == user.id.hex
        assert response.username == user.username
        assert response.avatar == generate_avatar(user.username)

    @pytest.mark.asyncio
    async def test_get_user_info__not_found(self, api, context):
        with pytest.raises(ApiException) as e:
            await api.GetUserInfo(UserId(id=uuid.uuid4().hex), context)

        assert e.value.response_type == ResponseType.ResourceNotFound

    @pytest.mark.asyncio
    async def test_get_user_detail__success(self, api, context, user: User):
        response = await api.GetUserDetail(UserId(id=user.id.hex), context)

        assert response.id == user.id.hex
        assert response.username == user.username
        assert response.avatar == generate_avatar(user.username)
        assert response.phone == user.phone
        assert response.create_time == datetime_to_timestamp(user.create_time)
        assert response.update_time == datetime_to_timestamp(user.update_time)

    @pytest.mark.asyncio
    async def test_get_user_detail__not_found(self, api, context):
        with pytest.raises(ApiException) as e:
            await api.GetUserDetail(UserId(id=uuid.uuid4().hex), context)

        assert e.value.response_type == ResponseType.ResourceNotFound

    @pytest.mark.asyncio
    async def test_list_user_info(self, api, context):
        count = 10

        uuids = [uuid.uuid4() for _ in range(count)]
        phones = list(random.sample(range(1000, 10000), count))

        users = []
        for i, uuid_ in enumerate(uuids):
            users.append(
                User(
                    id=uuid_,
                    username=f"test-username-{i}",
                    password=make_password("test-password"),
                    phone=f"1301234{phones[i]}",
                    last_login=timezone.now(),
                )
            )
        await User.objects.abulk_create(users)

        assert await User.objects.acount() == count

        request = UserIdList()
        request.ids.extend([_.hex for _ in uuids])

        response = await api.ListUserInfo(request, context)

        assert len(response.users) == count

        for user in response.users:
            assert uuid.UUID(user.id) in uuids

    @pytest.mark.asyncio
    async def test_list_user_info__empty(self, api, context):
        request = UserIdList()
        request.ids.extend([])

        response = await api.ListUserInfo(request, context)

        assert len(response.users) == 0

    @pytest.mark.asyncio
    async def test_list_user_info__not_found(self, api, context):
        request = UserIdList()
        request.ids.extend([uuid.uuid4().hex])

        response = await api.ListUserInfo(request, context)

        assert len(response.users) == 0

    @pytest.mark.asyncio
    async def test_update_user_avatar(self, api, context, user: User):
        request = UpdateUserAvatarRequest(
            id=user.id.hex,
            avatar="/user/avatar/test-avatar.jpg",
        )
        response = await api.UpdateUserAvatar(request, context)

        from django.conf import settings

        assert (
            response.avatar
            == f"{settings.MEDIA_URL}user/avatar/test-avatar.jpg"
        )
