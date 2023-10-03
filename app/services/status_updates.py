import logging

from app.constants import NotificationRequestLogStatus
from app.utilities import json_loads

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

        status = payload.get('status')
        message = payload.get('message') or None
        metadata = payload.get('metadata') or None
        operator = payload.get('operator') or None
        operator_event_id = payload.get('operator_event_id') or None
        sent_at = payload.get('sent_at')
        attempt_number = payload.get('attempt_number')
        channel = payload.get("channel")
        sent_to = payload.get("sent_to")

        await NotificationRequestLog.update_notification_log(
            payload['notification_log_id'], status=status, operator=operator, operator_event_id=operator_event_id,
            message=message, metadata=metadata
        )

        await NotificationRequestLog.upsert_attempt_log(
            payload["notification_log_id"],
            status=status,
            operator=operator,
            operator_event_id=operator_event_id,
            message=message,
            metadata=metadata,
            sent_at=sent_at,
            attempt_number=attempt_number,
            channel=channel,
            sent_to=sent_to
        )
        return True
