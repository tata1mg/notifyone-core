from typing import Optional, Dict
from tortoise_wrapper.wrappers import ORMWrapper
from torpedo.exceptions import BadRequestException
from app.exceptions import NotFoundException
from app.models.notification_core_db import SmsContentDBModel
from app.models.notification_core import SmsContentModel
from app.constants.database_tables import DatabaseTables
from app.utilities import utils
from app.constants.constants import Event
from app.constants.sms import Sms

class SmsContentRepository:

    @classmethod
    async def create_sms_entry(cls, sms: Dict):
        row = await ORMWrapper.create(SmsContentDBModel, sms)
        if not row:
            raise BadRequestException("new sms content cannot be inserted")
        return row

    @classmethod
    async def get_sms_content_from_event_id(cls, event_id: int) -> SmsContentModel:
        filters = {"event_id": event_id}
        sms_contents = await ORMWrapper.get_by_filters(
            SmsContentDBModel, filters=filters
        )
        if sms_contents:
            sms_content = await sms_contents[0].to_dict()
            return SmsContentModel(sms_content)
        return None

    @classmethod
    async def update_sms_template(cls, sms_id: int, to_update: Dict):
        where_clause = {"id": sms_id}
        updated_row = await ORMWrapper.update_with_filters(
            None, SmsContentDBModel, to_update, where_clause=where_clause
        )
        return updated_row

    @classmethod
    async def get_sms_templates(
        cls, event_id: Optional[int] = None, query_params: Optional[Dict] = None
    ):
        event_table = DatabaseTables.EVENT.value
        sms_table = DatabaseTables.SMS_CONTENT.value
        event_columns = Event.COLUMNS
        sms_columns = Sms.CONTENT_COLUMNS
        if query_params:
            size = query_params.get("size", Event.DEFAULT_LIMIT)
            start = query_params.get("start", Event.DEFAULT_OFFSET)
        else:
            size = Event.DEFAULT_LIMIT
            start = Event.DEFAULT_OFFSET
        # Prepare the SELECT clause for columns
        columns = [f"{event_table}.{column}" for column in event_columns] + [
            f"{sms_table}.{column}" for column in sms_columns
        ]
        # Prepare the JOIN condition
        join_condition = f"{event_table} JOIN {sms_table} ON {event_table}.id = {sms_table}.event_id WHERE {event_table}.is_deleted = False"
        if event_id:
            join_condition += f" AND {event_table}.id = {event_id}"
        else:
            where = utils.query_filters(query_params)
            join_condition += where
        # Prepare the complete SQL query
        query = f"SELECT {', '.join(columns)} FROM {join_condition} ORDER BY {event_table}.id DESC OFFSET {start} LIMIT {size}"
        # Execute the SQL query using the ORMWrapper
        sms_templates = await ORMWrapper.raw_sql(query)
        if not sms_templates:
            raise NotFoundException("No SMS template found")

        return sms_templates
