import asyncio
from app.constants import NotificationChannels, NotificationRequestLogStatus
from app.models.notification_core import EventModel
from app.repositories.content_log import ContentLogRepository
from app.repositories.notification_request_log import NotificationRequestLogRepository
from app.repositories.notification_request_attempt import (
    NotificationRequestAttemptRepository,
)
from app.utilities import json_dumps, current_utc_timestamp


class NotificationRequestLog:
    @classmethod
    async def log_notification_request_for_channel(cls, event: EventModel, channel: NotificationChannels, request_body):
        "Log notification request for a channel"
        send_addresses = NotificationChannels.get_sent_to_for_channel(channel.value, request_body)
        sent_to = ",".join(send_addresses)
        source_identifier = NotificationChannels.get_source_identifier_for_event(request_body)
        return (await NotificationRequestLogRepository.log_new_notification_request(
            event.id, request_body['request_id'], channel.value, sent_to, source_identifier
        ))

    @classmethod
    async def log_notification_request(cls, event: EventModel, request_body: dict = None):
        """
        Log a new notification request - all eligible channels in the notification event
        """
        active_channels = event.get_active_channels()
        log_tasks = list()
        for channel in active_channels:
            channel = NotificationChannels.get_enum(channel)
            log_tasks.append(cls.log_notification_request_for_channel(event, channel, request_body))
        result = await asyncio.gather(*log_tasks, return_exceptions=True)
        log_result = dict()
        for log_record_model in result:
            log_result[log_record_model.channel] = log_record_model
        return log_result

    @classmethod
    async def update_notification_log(cls, log_id, **kwargs):
        update_data = dict()
        if kwargs.get('status'):
            update_data['status'] = kwargs['status']
        if kwargs.get('message'):
            update_data['message'] = kwargs['message']
        if kwargs.get('operator'):
            update_data['operator'] = kwargs['operator']
        if kwargs.get('operator_event_id'):
            update_data['operator_event_id'] = kwargs['operator_event_id']
        if kwargs.get('metadata'):
            update_data['metadata'] = json_dumps(kwargs['metadata'])
        if update_data:
            update_data['updated'] = current_utc_timestamp()

        return await NotificationRequestLogRepository.update_notification_request_log(log_id, **update_data)

    @classmethod
    async def upsert_attempt_log(cls, log_id, **data):
        attempt_data = {}
        attempt_data["status"] = data.get("status")
        attempt_data["message"] = data.get("message")
        attempt_data["operator"] = data.get("operator")
        attempt_data["operator_event_id"] = data.get("operator_event_id")
        attempt_data["metadata"] = data.get("metadata")
        attempt_data["sent_at"] = data.get("sent_at")
        attempt_data["attempt_number"] = data.get("attempt_number")
        attempt_data["sent_to"] = data.get("sent_to")
        attempt_data["channel"] = data.get("channel")
        attempt_data["updated"] = current_utc_timestamp()
        await NotificationRequestAttemptRepository.log_new_notification_attempt(
            log_id, **attempt_data
        )

    @classmethod
    async def update_notification_request_processed_status(cls, log_id, **kwargs):
        """
        As we have already dispatched the notification request (to the handler), there is a chance that notification
        request has already been updated (to any of the
        NotificationRequestLogStatus.allowed_statuses_for_status_update() statuses) by the status update callback.
        We need to handle this case in our update query by putting the status not in clause.
        """
        update_data = dict()
        if kwargs.get('status'):
            update_data['status'] = kwargs['status']
        if kwargs.get('message'):
            update_data['message'] = kwargs['message']
        update_data['updated'] = current_utc_timestamp()
        where_clause = {
            'id': log_id,
            'status__in': NotificationRequestLogStatus.allowed_statues_for_processed_status_update()
        }

        channel = kwargs.get("channel")
        content = kwargs.get("content")
        request_id = kwargs.get("request_id")
        message = kwargs.get("message")
        tasks = [
            ContentLogRepository.create(request_id, channel, content, message),
            NotificationRequestLogRepository.update_notification_request_with_where_clause(
                where_clause, **update_data
            )
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)

    @classmethod
    async def get_triggered_count_for_limit_check(cls, event: EventModel, request_body: dict) -> dict:
        counts = {_channel: 0 for _channel in event.get_active_channels()}
        source_identifier = NotificationChannels.get_source_identifier_for_event(request_body)
        if source_identifier:
            triggered_notifications = await NotificationRequestLogRepository.get_notification_request_log(
                source_identifier=source_identifier, event_id=event.id)
            for notification_log in triggered_notifications:
                if notification_log.channel in counts:
                    counts[notification_log.channel] += 1
        return counts

    @classmethod
    async def get_already_triggered_channels(cls, notification_request_id: str) -> list:
        triggered_notifications = await NotificationRequestLogRepository.get_notification_request_log(
            notification_request_id=notification_request_id
        )
        already_triggered_channels = list()
        for notification_log in triggered_notifications:
            if notification_log.status in NotificationRequestLogStatus.trigger_successful_statuses():
                already_triggered_channels.append(notification_log.channel)
        return list(set(already_triggered_channels))
