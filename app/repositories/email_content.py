from typing import Optional, Dict, List
from torpedo.exceptions import BadRequestException
from tortoise_wrapper.wrappers import ORMWrapper
from app.exceptions import NotFoundException
from app.models.notification_core import EmailContentModel
from app.models.notification_core_db import EmailContentDBModel
from app.constants.database_tables import DatabaseTables
from app.utilities import utils
from app.constants.constants import Event
from app.constants.email import Email

class EmailContentRepository:

    @classmethod
    async def get_email_content_from_event_id(cls, event_id) -> EmailContentModel:
        filters = {"event_id": event_id}
        email_contents = await ORMWrapper.get_by_filters(
            EmailContentDBModel, filters=filters
        )
        if email_contents:
            email_content = await email_contents[0].to_dict()
            return EmailContentModel(email_content)
        return None

    @classmethod
    async def get_email_content_from_template_ids(
        cls, template_ids: List
    ) -> EmailContentModel:
        filters = {"id__in": template_ids}
        email_contents = await ORMWrapper.get_by_filters(
            EmailContentDBModel,
            filters=filters,
            order_by=None,
            limit=100,
            offset=0,
            only=None,
        )
        return [
            EmailContentModel(await email_content.to_dict())
            for email_content in email_contents
        ]

    @classmethod
    async def get_email_content_from_template_id(cls, id) -> EmailContentModel:
        filters = {"id": id}
        email_contents = await ORMWrapper.get_by_filters(
            EmailContentDBModel, filters=filters
        )
        if email_contents:
            email_content = await email_contents[0].to_dict()
            return EmailContentModel(email_content)
        return None

    @classmethod
    async def get_all_non_event_email_content(cls) -> [EmailContentModel]:
        filters = {"event_id": None}
        email_contents = await ORMWrapper.get_by_filters(
            EmailContentDBModel, filters=filters, limit=1000
        )
        return [
            EmailContentModel(await email_content.to_dict())
            for email_content in email_contents
        ]

    @classmethod
    async def create_email_entry(cls, email: Dict):
        row = await ORMWrapper.create(EmailContentDBModel, email)
        if not row:
            raise BadRequestException("new email content cannot be inserted")
        return row

    @classmethod
    async def update_email_content(cls, template_id: int, to_update: Dict):
        where_clause = {"id": template_id}
        updated_row = await ORMWrapper.update_with_filters(
            None, EmailContentDBModel, to_update, where_clause=where_clause
        )
        return updated_row

    @classmethod
    async def get_email_templates(
        cls, event_id: Optional[int] = None, query_params: Optional[Dict] = None
    ):
        event_table = DatabaseTables.EVENT.value
        email_table = DatabaseTables.EMAIL_CONTENT.value
        event_columns = Event.COLUMNS
        email_columns = Email.CONTENT_COLUMNS
        if query_params:
            size = query_params.get("size", Event.DEFAULT_LIMIT)
            start = query_params.get("start", Event.DEFAULT_OFFSET)
        else:
            size = Event.DEFAULT_LIMIT
            start = Event.DEFAULT_OFFSET
        # Prepare the SELECT clause for columns
        columns = [f"{event_table}.{column}" for column in event_columns] + [
            f"{email_table}.{column}" for column in email_columns
        ]
        # Prepare the JOIN condition
        join_condition = f"{event_table} JOIN {email_table} ON {event_table}.id={email_table}.event_id WHERE {event_table}.is_deleted = False"
        if event_id:
            join_condition += f" AND {event_table}.id = {event_id}"
        else:
            where = utils.query_filters(query_params)
            join_condition += where
        # Prepare the complete SQL query
        query = f"SELECT {', '.join(columns)} FROM {join_condition} ORDER BY {event_table}.id DESC OFFSET {start} LIMIT {size}"
        # Execute the SQL query using the ORMWrapper
        email_templates = await ORMWrapper.raw_sql(query)
        if not email_templates:
            raise NotFoundException("No email template found")

        return email_templates

    @classmethod
    async def search_emails(cls, size, **search_dict):
        where_key = {
            key: ("ilike", "%{}%".format(val))
            for key, val in search_dict.items()
            if val
        }
        email_contents = await ORMWrapper.get_by_filters(
            EmailContentDBModel, filters=where_key, limit=size
        )
        return [
            EmailContentModel(await email_content.to_dict())
            for email_content in email_contents
        ]