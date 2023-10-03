import sys
from typing import Optional, Dict
from torpedo.exceptions import BadRequestException
from tortoise_wrapper.wrappers import ORMWrapper
from app.constants.database_tables import DatabaseTables
from app.caches import NotificationCoreCache
from app.models.notification_core import EventModel
from app.models.notification_core_db import EventDBModel
from app.utilities.decorators import redis_cache_decorator_custom
from app.exceptions import NotFoundException
from app.utilities import utils
from app.constants.constants import Event
from app.constants.email import Email
from app.constants.sms import Sms
from app.constants.whatsapp import Whatsapp
from app.constants.push import Push

class EventRepository:

    @staticmethod
    async def _convert_event_to_dict(event_from_db: EventDBModel) -> dict:
        event = await event_from_db.to_dict()
        event["created"] = event["created"].timestamp()
        event["updated"] = event["updated"].timestamp()
        return event

    @classmethod
    async def get_event(cls, app_name: str, event_name: str) -> EventModel:
        event = await cls.get_event_from_db(app_name, event_name)
        if event:
            return EventModel(event)
        return None

    @classmethod
    async def get_events(cls) -> [EventModel]:
        events = list()
        events_from_db = await cls.get_events_from_db()
        for event_dict in events_from_db:
            events.append(EventModel(event_dict))
        return events

    @classmethod
    @redis_cache_decorator_custom(NotificationCoreCache, expire_time=300)
    async def get_events_from_db(cls):
        events_from_db = await ORMWrapper.get_by_filters(
            EventDBModel, {}, limit=sys.maxsize
        )
        events_from_db = events_from_db or list()
        return [await cls._convert_event_to_dict(event) for event in events_from_db]

    @classmethod
    @redis_cache_decorator_custom(NotificationCoreCache, expire_time=300)
    async def get_event_from_db(cls, app_name: str, event_name: str) -> dict:
        filters = {"app_name": app_name, "event_name": event_name}
        events_from_db = await ORMWrapper.get_by_filters(EventDBModel, filters, limit=1)
        if events_from_db:
            return await cls._convert_event_to_dict(events_from_db[0])
        return dict()

    @classmethod
    async def create_event(cls, event_details: Dict):
        row = await ORMWrapper.create(EventDBModel, event_details)
        if not row:
            raise BadRequestException("new event cannot be inserted")
        return row

    @classmethod
    async def update_event(cls, app_name: str, event_name: str, values: Dict):
        where_clause = {"app_name": app_name, "event_name": event_name}
        updated_row = await ORMWrapper.update_with_filters(
            None, EventDBModel, values, where_clause=where_clause
        )
        return updated_row

    @classmethod
    async def update_event_with_id(cls, event_id: int, values: Dict):
        where_clause = {"id": event_id}
        updated_row = await ORMWrapper.update_with_filters(
            None, EventDBModel, values, where_clause=where_clause
        )
        return updated_row

    @classmethod
    async def get_event_details(cls, app_name: Optional[str] = None, event_name: Optional[str] = None) -> dict:
        filters = dict()
        if app_name:
            filters['app_name'] = app_name
        if event_name:
            filters['event_name'] = event_name    
        events_from_db = await ORMWrapper.get_by_filters(EventDBModel, filters, limit=1)
        if events_from_db:
            return await cls._convert_event_to_dict(events_from_db[0])
        return None

    @classmethod
    async def get_events_by_id(cls, event_id: int) -> EventModel:
        filters = {"id": event_id}
        queryset = await ORMWrapper.get_by_filters(EventDBModel, filters=filters)
        if queryset:
            queryset = await queryset[0].to_dict()
            return EventModel(queryset)
        return None

    @classmethod
    async def get_all_templates(
        cls, id: Optional[int] = None, query_params: Optional[Dict] = None
    ):
        event_table, sms_table, email_table, push_notification, whatsapp_table = (
            DatabaseTables.EVENT.value,
            DatabaseTables.SMS_CONTENT.value,
            DatabaseTables.EMAIL_CONTENT.value,
            DatabaseTables.PUSH_NOTIFICATION.value,
            DatabaseTables.WHATSAPP_CONTENT.value,
        )
        event_columns = Event.COLUMNS
        sms_columns = Sms.CONTENT_COLUMNS
        email_columns = Email.CONTENT_COLUMNS
        push_columns = Push.CONTENT_COLUMNS
        whatsapp_columns = Whatsapp.CONTENT_COLUMNS
        if query_params:
            size = query_params.get("size", Event.DEFAULT_LIMIT)
            start = query_params.get("start", Event.DEFAULT_OFFSET)
        else:
            size = Event.DEFAULT_LIMIT
            start = Event.DEFAULT_OFFSET
        event_id = Event.EVENT_ID
        columns = [
            f"{event_table}.{column} as event_{column}" for column in event_columns
        ]
        columns += [
            f"{sms_table}.{column} as sms_{column}"
            for column in sms_columns
            if column != event_id
        ]
        columns += [
            f"{email_table}.{column} as email_{column}"
            for column in email_columns
            if column != event_id
        ]
        columns += [
            f"{push_notification}.{column} as push_{column}"
            for column in push_columns
            if column != event_id
        ]
        columns += [
            f"{whatsapp_table}.{column} as whatsapp_{column}"
            for column in whatsapp_columns
            if column != event_id
        ]
        columns.append(f"event.id as {event_table}_id")
        columns = ", ".join(columns)
        join_condition = (
            f"{event_table} LEFT JOIN {sms_table} ON {event_table}.id={sms_table}.event_id "
            f"LEFT JOIN {email_table} ON {event_table}.id={email_table}.event_id "
            f"LEFT JOIN {push_notification} ON {event_table}.id={push_notification}.event_id "
            f"LEFT JOIN {whatsapp_table} ON {event_table}.id={whatsapp_table}.event_id "
            f"where {event_table}.is_deleted = False "
        )
        if id:
            join_condition += f" AND {event_table}.id = {id}"
        else:
            where = utils.query_filters(query_params)
            join_condition += where
        query = (
            f"select {columns} from {join_condition} "
            f"order by {event_table}.id desc offset {start} limit {size}"
        )
        all_templates = await ORMWrapper.raw_sql(query)
        if not all_templates:
            raise NotFoundException("no templates found")
        return all_templates
        