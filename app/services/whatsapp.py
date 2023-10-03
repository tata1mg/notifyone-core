from typing import List
import logging
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
    dispatch_notification_request_common_payload,
    is_notification_allowed_for_mobile,
)
from .abstract_handler import AbstractHandler
from .logging import NotificationRequestLog
from app.repositories.whatsapp_content import WhatsappContentRepository
logger = logging.getLogger()

class WhatsappHandler(AbstractHandler):
    _dispatch_notification_config = CONFIG.config["DISPATCH_NOTIFICATION_REQUEST"]
    _channel_config = _dispatch_notification_config["WHATSAPP"]

    @classmethod
    async def handle(
        cls, event: EventModel, request_body, notification_request_log_row
    ):
        # TODO Push to SNS
        # TODO Update analytics log
        unhandled_exception = False
        status = NotificationRequestLogStatus.INITIATED
        message = None
        template = None
        body_values = None
        try:
            send_address = NotificationChannels.get_sent_to_for_channel(
                NotificationChannels.WHATSAPP.value, request_body
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

            request_body = request_body or dict()
            phone_number = send_address
            whatsapp_channel_data = request_body["channels"]["whatsapp"]
            body_values = whatsapp_channel_data.get("body_values", [])
            attachments = request_body.get("attachments")
            data = dispatch_notification_request_common_payload(
                event.id,
                event.event_name,
                event.app_name,
                NotificationChannels.WHATSAPP.value,
                notification_request_log_row.id,
            )
            whatsapp_data = (
                await WhatsappContentRepository.get_whatsapp_content_from_event_id(event.id)
            )
            template = whatsapp_data.name
            # template = event.get_whatsapp_template_name()
            data.update(
                {
                    "template": template,
                    "body_values": body_values,
                    "mobile": phone_number,
                }
            )
            if attachments:
                data.update(
                    {
                        "files": attachments,
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
                content=cls._get_content(template, body_values),
                channel=NotificationChannels.WHATSAPP,
                request_id=request_body["request_id"],
            )
        if unhandled_exception:
            raise Exception("Unhandled exception in sending push")
        return result

    @classmethod
    def _get_content(self, template: str, body_values: List[str]):
        return f"templateName: {template}\nValues: {body_values}"
