import logging
import asyncio
from torpedo import CONFIG
from app.constants import (
    NotificationChannels,
    NotificationRequestLogStatus,
    ErrorMessages,
)
from app.exceptions import NoSendAddressFoundException
from app.models.notification_core import EventModel
from app.service_clients.publisher import PublishResult
from app.utilities import (
    get_transformed_message_by_text,
    dispatch_notification_request_common_payload,
    is_notification_allowed_for_mobile,
)
from .abstract_handler import AbstractHandler
from .logging import NotificationRequestLog
from app.repositories.sms_content import SmsContentRepository

logger = logging.getLogger()

class SMSHandler(AbstractHandler):
    _dispatch_notification_config = CONFIG.config["DISPATCH_NOTIFICATION_REQUEST"]
    _channel_config = _dispatch_notification_config["SMS"]

    @classmethod
    async def handle(
        cls, event: EventModel, request_body, notification_request_log_row
    ):
        # TODO Push to SNS
        # TODO Update analytics log
        unhandled_exception = False
        status = NotificationRequestLogStatus.INITIATED
        message = None
        notification_body = None
        try:
            send_address = NotificationChannels.get_sent_to_for_channel(
                NotificationChannels.SMS.value, request_body
            )
            if not send_address:
                raise NoSendAddressFoundException(
                    ErrorMessages.NO_SEND_ADDRESS_FOUND.value
                )

            # Currently, we support only one mobile id in send_address
            send_address = send_address[0]

            if not is_notification_allowed_for_mobile(send_address):
                raise NoSendAddressFoundException(
                    ErrorMessages.SEND_ADDRESS_NOT_ALLOWED_ON_TEST_ENV.value
                )

            notification_body = await cls.get_sms_body(event, request_body)
            data = dispatch_notification_request_common_payload(
                event.id,
                event.event_name,
                event.app_name,
                NotificationChannels.SMS.value,
                notification_request_log_row.id,
            )
            data.update(
                {
                    "message": notification_body,
                    "to": send_address,
                    "channel": request_body.get("channel", ""),
                }
            )
            result = await cls._dispatch_notification.publish(
                payload=data, priority=event.priority
            )
        except NoSendAddressFoundException as ne:
            status = NotificationRequestLogStatus.NOT_ELIGIBLE
            message = str(ne)
            result = PublishResult(is_success=False, status=status, message=message)
        except Exception as e:
            status = NotificationRequestLogStatus.FAILED
            message = str(e)
            result = PublishResult(is_success=False, status=status, message=message)
            result.unhandled_exception = True
            logger.exception(e)
        finally:
            # update notification request log status
            await NotificationRequestLog.update_notification_request_processed_status(
                notification_request_log_row.id,
                message=message,
                status=status.value,
                content=notification_body,
                channel=NotificationChannels.SMS,
                request_id=request_body["request_id"],
            )
        return result

    @classmethod
    async def get_sms_body(cls, event: EventModel, request_body: dict):
        sms_data = await SmsContentRepository.get_sms_content_from_event_id(event.id)
        sms_template = sms_data.content
        return await get_transformed_message_by_text(sms_template, request_body["body"])
