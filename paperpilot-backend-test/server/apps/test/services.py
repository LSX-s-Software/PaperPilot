import uuid

from django.utils import timezone
from paperpilot_common.helper.field import datetime_to_timestamp
from paperpilot_common.protobuf.test.test_pb2 import TestResult
from paperpilot_common.protobuf.user.user_pb2 import UserId
from paperpilot_common.utils.log import get_logger

from server.business.grpc import user_client


class TestService:
    logger = get_logger("test.service")

    @property
    def user_service(self):
        return user_client.stub

    async def get_anonymous_test(self) -> TestResult:
        # try:
        #     0 / 0
        # except Exception as e:
        #     raise ApiException(
        #         ResponseType.ClientError, msg="test error", inner=e, record=True
        #     )
        self.logger.debug("anonymous test")
        return TestResult(time=datetime_to_timestamp(timezone.now()), user=None)

    async def get_user_test(self, user_id: uuid.UUID) -> TestResult:
        self.logger.debug(f"user test: {user_id}")
        user_info = await self.user_service.GetUserInfo(UserId(id=user_id.hex))
        return TestResult(
            time=datetime_to_timestamp(timezone.now()), user=user_info
        )


test_service: TestService = TestService()
