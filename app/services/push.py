import json
import logging
from torpedo import CONFIG
from app.constants import (
    NotificationChannels,
    NotificationRequestLogStatus,
    ErrorMessages,
)
from app.constants.constants import MAX_DEVICES_FOR_PUSH
from app.exceptions import ResourceNotFoundException, NoSendAddressFoundException
from app.models.notification_core import EventModel
from app.repositories.push_notification import PushNotificationRepository
from app.service_clients.publisher import PublishResult
from app.utilities import (
    render_text,
    dispatch_notification_request_common_payload,
    is_notification_allowed_for_email,
)
from .abstract_handler import AbstractHandler
from .logging import NotificationRequestLog

dispatch_notification_config = CONFIG.config["DISPATCH_NOTIFICATION_REQUEST"]


logger = logging.getLogger()


class PushHandler(AbstractHandler):
    _dispatch_notification_config = CONFIG.config["DISPATCH_NOTIFICATION_REQUEST"]
    _channel_config = _dispatch_notification_config["PUSH"]

    @classmethod
    async def handle(
        cls, event: EventModel, request_body, notification_request_log_row
    ):
        # TODO Push to SNS
        # TODO Update analytics log
        unhandled_exception = False
        status = NotificationRequestLogStatus.INITIATED
        message = None
        push_data = None
        try:
            push_detail = await PushNotificationRepository.get_push_notification(
                event.id
            )

            if not push_detail:
                raise ResourceNotFoundException(
                    ErrorMessages.PUSH_EVENT_NOT_FOUND_IN_DB.value
                )

            send_address = NotificationChannels.get_sent_to_for_channel(
                NotificationChannels.PUSH.value, request_body
            )
            if not send_address:
                raise NoSendAddressFoundException(
                    ErrorMessages.NO_SEND_ADDRESS_FOUND.value
                )

            devices = list()
            for device in send_address:
                d = {"register_id": device}
                devices.append(d)

            push_data = {
                "title": await render_text(push_detail.title, request_body["body"]),
                "body": await render_text(push_detail.body, request_body["body"]),
                "target": await render_text(push_detail.target, request_body["body"]),
                "image": await render_text(push_detail.image, request_body["body"]),
                "registered_devices": devices,
            }
            data = dispatch_notification_request_common_payload(
                event.id,
                event.event_name,
                event.app_name,
                NotificationChannels.PUSH.value,
                notification_request_log_row.id,
            )
            data.update({"push_data": push_data})
            # Pushing directly to SQS. Need to integrate SNS
            result = await cls._dispatch_notification.publish(
                payload=data, priority=event.priority
            )
        except (ResourceNotFoundException, NoSendAddressFoundException) as r:
            status = NotificationRequestLogStatus.NOT_ELIGIBLE
            message = str(r)
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
                content=json.dumps(push_data),
                channel=NotificationChannels.PUSH,
                request_id=request_body["request_id"],
            )
        if unhandled_exception:
            raise Exception("Unhandled exception in sending push")
        return result
