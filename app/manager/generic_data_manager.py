import logging
from typing import List, Optional, Dict
from app.repositories.generic_data_store import GenericDataRepository
from app.exceptions import NotFoundException

logger = logging.getLogger()

class GenericDataStoreManager:

    @staticmethod
    async def update_or_insert_data_store_entry(
        event_id: str, data: Dict, updated_by: Optional[str] = None
    ):
        updated_by = updated_by or "notification_core"
        record = await GenericDataRepository.get_data_store_entry(
            event_id, category="event_body"
        )
        if record:
            await GenericDataRepository.update_data_store_entry(
                event_id, data, updated_by, category="event_body"
            )
        else:
            await GenericDataRepository.create_data_store_entry(
                event_id, data, created_by=updated_by, category="event_body"
            )

    @classmethod
    async def get_event_body(cls, event_id: int):
        entry_data = await GenericDataRepository.get_data_store_entry(
            event_id, category="event_body"
        )
        if entry_data.data:
            return entry_data.data
        else:
            raise NotFoundException(
                "data not found"
            )
