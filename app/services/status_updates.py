import logging

from app.constants import NotificationRequestLogStatus
from app.utilities import json_loads
from app.services.webhooks import WebhookController

from .logging import NotificationRequestLog

logger = logging.getLogger()


class NotificationStatusUpdate:
    @classmethod
    async def handle_status_update(cls, payload, subscriber_id, message_receive_count=1):
        try:
            payload = json_loads(payload)
        except Exception as e:
            logger.error('Invalid status update payload received. Payload must be valid json object')
            return True
        if not (payload.get('notification_log_id') and payload.get('status')):
            logger.exception("Missing required params in the status update payload. Payload - {}".format(payload))
            return True
        if payload.get('status') not in NotificationRequestLogStatus.allowed_statuses_for_status_update():
            logger.exception("Invalid status value received in the status update payload. Payload - {}".format(payload))
            return True

        notification_log_id = payload['notification_log_id']
        status = payload.get('status')
        message = payload.get('message') or None
        metadata = payload.get('metadata') or None
        operator = payload.get('operator') or None
        operator_event_id = payload.get('operator_event_id') or None
        sent_at = payload.get('sent_at')
        attempt_number = payload.get('attempt_number')
        channel = payload.get("channel")
        sent_to = payload.get("sent_to")
        source = payload.get("source")
        detail = payload.get("detail")

        await NotificationRequestLog.update_notification_log(
            notification_log_id, status=status, operator=operator, operator_event_id=operator_event_id,
            message=message, source=source, metadata=metadata, channel_status=detail
        )

        await NotificationRequestLog.upsert_attempt_log(
            notification_log_id,
            status=status,
            operator=operator,
            operator_event_id=operator_event_id,
            message=message,
            metadata=metadata,
            sent_at=sent_at,
            attempt_number=attempt_number,
            channel=channel,
            source=source,
            sent_to=sent_to,
            channel_status=detail
        )

        await WebhookController.handle_webhook(
            status=status,
            source=source,
            channel=channel,
            timestamp=sent_at,
            channel_status=detail,
            log_id=notification_log_id,
            attempt_number=attempt_number,
            operator_event_id=operator_event_id,
        )
        return True
