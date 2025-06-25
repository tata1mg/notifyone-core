import json
import logging
from typing import Callable, List
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
from app.service_clients import AuthClient
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

            devices = await cls.get_devices(request_body)

            registered_devices = list()
            for device in devices:
                d = {
                    "user_id": device.get("user_id"),
                    "device_id": device.get("device_id"),
                    "device_os": device.get("device_os"),
                    "device_os_type": device.get("device_os_type"),
                    "register_id": device.get("register_id"),
                    "voip_token": device.get("voip_token"),
                    "device_token": device.get("device_token"),
                    "live_notification_token": (
                        device.get("metadata")
                        if isinstance(device.get("metadata"), dict)
                        else {}
                    ).get("live_notification_token", {}),
                    "app_id": device.get("app_id"),
                    "application_name": device.get("application_name"),
                }
                registered_devices.append(d)

            push_data = {
                "title": await render_text(push_detail.title, request_body["body"]),
                "body": await render_text(push_detail.body, request_body["body"]),
                "target": await render_text(push_detail.target, request_body["body"]),
                "image": await render_text(push_detail.image, request_body["body"]),
                "details": request_body["push"],
                "type": push_detail.type,
                "registered_devices": registered_devices,
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
                message=result.message,
                status=result.status.value,
                content=json.dumps(push_data),
                channel=NotificationChannels.PUSH,
                request_id=request_body["request_id"],
            )
        if unhandled_exception:
            raise Exception("Unhandled exception in sending push")
        return result
    
    @classmethod
    async def get_devices(cls, request_body):
        """
        Get devices from the given list of recipients,
        if not available then fetch from identity service using the email address
        """

        devices = request_body.get("to", {}).get("devices")
        if devices:
            return devices

        send_address = NotificationChannels.get_sent_to_for_channel(
            NotificationChannels.PUSH.value, request_body
        )
        if not send_address:
            raise NoSendAddressFoundException(ErrorMessages.NO_SEND_ADDRESS_FOUND.value)

        if not is_notification_allowed_for_email(send_address):
            raise NoSendAddressFoundException(
                ErrorMessages.SEND_ADDRESS_NOT_ALLOWED_ON_TEST_ENV.value
            )

        # The devices list received from auth is sorted on created data.
        devices = await AuthClient.get_devices_by_email_id(send_address)
        if devices and not devices["devices"]:
            raise ResourceNotFoundException(
                ErrorMessages.NO_REGISTERED_DEVICE_FOUND.value
            )

        # Consider max 5 devices created recently.
        return devices["devices"][-MAX_DEVICES_FOR_PUSH::]

    @classmethod
    async def get_push_content(cls, event: EventModel, _body: dict):
        push_detail = await PushNotificationRepository.get_push_notification(event.id)
        push_data = {
                "title": await render_text(push_detail.title, _body["body"]),
                "body": await render_text(push_detail.body, _body["body"]),
                "target": await render_text(push_detail.target, _body["body"]),
                "image": await render_text(push_detail.image, _body["body"]),
                "type": push_detail.type
            }
        return push_data

