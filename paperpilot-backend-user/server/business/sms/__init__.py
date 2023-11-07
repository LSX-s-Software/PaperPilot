import json

from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_dysmsapi20170525.client import (
    Client as Dysmsapi20170525Client,
)
from alibabacloud_tea_openapi import models as open_api_models
from paperpilot_common.exceptions import ApiException
from paperpilot_common.response import ResponseType
from paperpilot_common.utils.log import get_logger

from .cache import sms_cache
from .config import (
    access_key_id,
    access_key_secret,
    enable,
    sign_name,
    template,
)


class SmsBusiness:
    """
    短信业务
    """

    logger = get_logger("business.sms")
    client = Dysmsapi20170525Client(
        open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint="dysmsapi.aliyuncs.com",
        )
    )
    enable = enable

    async def _send(
        self,
        phone_numbers: str = None,
        sign_name: str = None,
        template_code: str = None,
        template_param: str = None,
    ):
        """
        发送短信

        :param phone_numbers: 接收短信的手机号码
        :param sign_name: 短信签名名称
        :param template_code: 短信模板ID
        :param template_param: 短信模板变量对应的实际值，JSON格式
        """

        if await sms_cache.check_phone(phone_numbers):
            self.logger.debug(f"frequency limit, phone: {phone_numbers}")
            raise ApiException(
                ResponseType.APIThrottled,
                detail="发送短信过于频繁，请1分钟后再试",
                record=False,
            )

        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=phone_numbers,
            sign_name=sign_name,
            template_code=template_code,
            template_param=template_param,
        )

        try:
            self.logger.info(f"send sms, phone: {phone_numbers}")

            if not self.enable:
                self.logger.warning("短信功能未开启")
                self.logger.debug(
                    f"send fake sms, "
                    f"phone: {phone_numbers}, "
                    f"template_param: {template_param}, "
                    f"sign_name: {sign_name}, "
                    f"template_code: {template_code}"
                )
                await sms_cache.add_phone(phone_numbers)
                return

            result = await self.client.send_sms_async(send_sms_request)

            if result.body.code != "OK":
                self.logger.error(
                    f"send sms failed, phone: {phone_numbers}, "
                    f"result: {result.body}"
                )
                raise ApiException(
                    ResponseType.ThirdServiceError,
                    detail=result.body.message,
                )

            await sms_cache.add_phone(phone_numbers)
            self.logger.info(
                f"send sms success, phone: {phone_numbers}, result: {result.body}"
            )
        except Exception as e:
            self.logger.error(f"send sms failed, phone: {phone_numbers}")
            if isinstance(e, ApiException):
                raise e
            raise ApiException(
                ResponseType.ThirdServiceError, inner=e, detail="发送短信失败"
            )

    async def send_code(self, phone: str, code: str):
        """
        发送验证码

        :param phone: 手机号
        :param code: 验证码
        """
        self.logger.debug(f"send sms code, phone: {phone}, code: {code}")
        await self._send(
            phone_numbers=phone,
            sign_name=sign_name,
            template_code=template["code"],
            template_param=json.dumps({"code": code}),
        )


sms_business: SmsBusiness = SmsBusiness()
