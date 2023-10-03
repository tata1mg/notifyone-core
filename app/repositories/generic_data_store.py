import json
from torpedo.exceptions import BadRequestException
from app.models.notification_core import GenericDataStoreModel
from app.models.notification_core_db import GenericDataStoreDBModel
from tortoise_wrapper.wrappers import ORMWrapper

class GenericDataRepository:

    @classmethod
    async def get_data_store_entry(
        cls, event_id: int, category: str
    ) -> GenericDataStoreModel:
        filters = {"event_id": event_id, "category": category}
        queryset = await ORMWrapper.get_by_filters(GenericDataStoreDBModel, filters)
        if not queryset:
            return None
        event_data = await queryset[0].to_dict()
        return GenericDataStoreModel(event_data)

    @classmethod
    async def update_data_store_entry(
        cls, event_id, data, updated_by, category
    ) -> GenericDataStoreModel:
        to_update = {"updated_by": updated_by, "data": json.dumps(data)}
        where_clause = {"event_id": event_id, "category": category}
        updated_row = await ORMWrapper.update_with_filters(
            None, GenericDataStoreDBModel, to_update, where_clause=where_clause
        )
        return updated_row

    @classmethod
    async def create_data_store_entry(cls, event_id, data, created_by, category):
        data_details = {
            "event_id": event_id,
            "category": category,
            "identifier": event_id,
            "data": json.dumps(data),
            "updated_by": created_by,
        }
        row = await ORMWrapper.create(GenericDataStoreDBModel, data_details)
        if not row:
            raise BadRequestException(
                "new data cannot be inserted in generic_data_store table"
            )
        return row
        