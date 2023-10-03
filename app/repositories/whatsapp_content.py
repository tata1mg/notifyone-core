from typing import Optional, Dict
from tortoise_wrapper.wrappers import ORMWrapper
from torpedo.exceptions import BadRequestException
from app.exceptions import NotFoundException
from app.models.notification_core_db import WhatsappContentDBModel
from app.models.notification_core import WhatsappContentModel
from app.constants.database_tables import DatabaseTables
from app.constants.constants import Event
from app.constants.whatsapp import Whatsapp
from app.utilities import utils

class WhatsappContentRepository:
    @classmethod
    async def create_whatsapp_entry(cls, whatsapp: Dict):
        row = await ORMWrapper.create(WhatsappContentDBModel, whatsapp)
        if not row:
            raise BadRequestException("new whatsapp content cannot be inserted")
        return row

    @classmethod
    async def get_whatsapp_content_from_event_id(
        cls, event_id: int
    ) -> WhatsappContentModel:
        filters = {"event_id": event_id}
        whatsapp_contents = await ORMWrapper.get_by_filters(
            WhatsappContentDBModel, filters=filters
        )
        if whatsapp_contents:
            whatsapp_contents = await whatsapp_contents[0].to_dict()
            return WhatsappContentModel(whatsapp_contents)
        return None

    @classmethod
    async def update_whatsapp_table(cls, whatsapp_template_id: int, to_update: Dict):
        where_clause = {"id": whatsapp_template_id}
        updated_row = await ORMWrapper.update_with_filters(
            None, WhatsappContentDBModel, to_update, where_clause=where_clause
        )
        return updated_row

    @classmethod
    async def get_whatsapp_templates(
        cls, event_id: Optional[int] = None, query_params: Optional[Dict] = None
    ):
        event_table = DatabaseTables.EVENT.value
        whatsapp_table = DatabaseTables.WHATSAPP_CONTENT.value
        event_columns = Event.COLUMNS
        whatsapp_columns = Whatsapp.CONTENT_COLUMNS
        if query_params:
            size = query_params.get("size", Event.DEFAULT_LIMIT)
            start = query_params.get("start", Event.DEFAULT_OFFSET)
        else:
            size = Event.DEFAULT_LIMIT
            start = Event.DEFAULT_OFFSET
        # Prepare the SELECT clause for columns
        columns = [f"{event_table}.{column}" for column in event_columns] + [
            f"{whatsapp_table}.{column}" for column in whatsapp_columns
        ]
        # Prepare the JOIN condition
        join_condition = f"{event_table} JOIN {whatsapp_table} ON {event_table}.id = {whatsapp_table}.event_id WHERE {event_table}.is_deleted = False"
        if event_id:
            join_condition += f" AND {event_table}.id = {event_id}"
        else:
            where = utils.query_filters(query_params)
            join_condition += where
        # Prepare the complete SQL query
        query = f"SELECT {', '.join(columns)} FROM {join_condition} ORDER BY {event_table}.id DESC OFFSET {start} LIMIT {size}"
        # Execute the SQL query using the ORMWrapper
        whatsapp_templates = await ORMWrapper.raw_sql(query)
        if not whatsapp_templates:
            raise NotFoundException("No WhatsApp template found")
        return whatsapp_templates
