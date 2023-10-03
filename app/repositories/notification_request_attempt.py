from datetime import datetime
from tortoise_wrapper.wrappers import ORMWrapper

from app.models.notification_core_db import NotificationRequestAttemptDBModel


class NotificationRequestAttemptRepository:
    @classmethod
    async def log_new_notification_attempt(
        cls,
        log_id,
        message,
        channel,
        sent_to,
        operator,
        operator_event_id,
        status,
        attempt_number,
        sent_at,
        metadata,
        updated,
    ):
        log_data = {
            "channel": channel,
            "operator": operator,
            "operator_event_id": operator_event_id,
            "status": status,
            "message": message,
            "sent_at": datetime.strptime(sent_at, "%B %d, %Y %H:%M:%S"),
            "metadata": metadata,
            "updated": updated,
        }
        # `-1` represents log_id is unkown in this update
        # Trying to identify the row using operator_event_id
        if log_id == "-1":
            await cls.update_notification_attempt(operator_event_id, log_data)
        else:
            log_data.update(
                {
                    "log_id": log_id,
                    "sent_to": sent_to,
                    "attempt_number": attempt_number,
                }
            )
            await cls.insert_notification_attempt(log_data)

    @classmethod
    async def update_notification_attempt(cls, operator_event_id, log_data):
        where = {"operator_event_id": operator_event_id}
        return await ORMWrapper.update_with_filters(
            None, NotificationRequestAttemptDBModel, log_data, where_clause=where
        )

    @classmethod
    async def insert_notification_attempt(cls, log_data):
        return await ORMWrapper.create(NotificationRequestAttemptDBModel, log_data)
