from typing import Optional, Dict
from torpedo.exceptions import BadRequestException
from tortoise_wrapper.wrappers import ORMWrapper
from app.constants.constants import Event
from app.constants.push import Push
from app.exceptions import NotFoundException
from app.models.notification_core import PushNotificationModel
from app.models.notification_core_db import PushNotificationDBModel
from app.constants.database_tables import DatabaseTables
from app.utilities import utils

class PushNotificationRepository:

    @classmethod
    async def get_push_notification(cls, event_id: int) -> PushNotificationModel:
        filters = {"event_id": event_id}
        push_notifications = await ORMWrapper.get_by_filters(
            PushNotificationDBModel, filters, limit=1
        )
        if push_notifications:
            push_notification_dict = await push_notifications[0].to_dict()
            return PushNotificationModel(push_notification_dict)
        return None

    @classmethod
    async def create_push_notification_entry(cls, push: Dict):
        row = await ORMWrapper.create(PushNotificationDBModel, push)
        if not row:
            raise BadRequestException("new push_notification cannot be inserted")
        return row

    @classmethod
    async def update_push_notification(cls, notification_id: int, to_update: Dict):
        where_clause = {"id": notification_id}
        updated_row = await ORMWrapper.update_with_filters(
            None, PushNotificationDBModel, to_update, where_clause=where_clause
        )
        return updated_row

    @classmethod
    async def get_push_notification_templates(
        cls, event_id: Optional[int] = None, query_params: Optional[Dict] = None
    ):
        event_table = DatabaseTables.EVENT.value
        push_notification = DatabaseTables.PUSH_NOTIFICATION.value
        event_columns = Event.COLUMNS
        push_notification_columns = Push.CONTENT_COLUMNS
        if query_params:
            size = query_params.get("size", Event.DEFAULT_LIMIT)
            start = query_params.get("start", Event.DEFAULT_OFFSET)
        else:
            size = Event.DEFAULT_LIMIT
            start = Event.DEFAULT_OFFSET
        # Prepare the SELECT clause for columns
        columns = [f"{event_table}.{column}" for column in event_columns] + [
            f"{push_notification}.{column}" for column in push_notification_columns
        ]
        # Prepare the JOIN condition
        join_condition = f"{event_table} JOIN {push_notification} ON {event_table}.id = {push_notification}.event_id WHERE {event_table}.is_deleted = False"
        if event_id:
            join_condition += f" AND {event_table}.id = {event_id}"
        else:
            where = utils.query_filters(query_params)
            join_condition += where
        # Prepare the complete SQL query
        query = f"SELECT {', '.join(columns)} FROM {join_condition} ORDER BY {event_table}.id DESC OFFSET {start} LIMIT {size}"
        # Execute the SQL query using the ORMWrapper
        notifications = await ORMWrapper.raw_sql(query)
        if not notifications:
            raise NotFoundException("No push template found")

        return notifications