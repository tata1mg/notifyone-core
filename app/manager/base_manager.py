import json
from typing import List, Optional, Dict
from app.exceptions import BadRequestException
from app.repositories.event import EventRepository
from app.utilities.utils import check_format


class BaseManager:
    @classmethod
    async def update_trigger_limit(cls, event_type: str, agent_id: str, **kwargs):
        app_name = kwargs["payload"].get("app_name")
        event_name = kwargs["payload"].get("event_name")
        event_id = kwargs["payload"].get("event_id")
        data = await cls.common_validation_checks(app_name, event_name, event_id)
        event_limit = kwargs["payload"].get("triggers_limit")

        if event_limit:
            triggers_limit = data.triggers_limit
            # as in some cases trigger_limit is instance of str.
            triggers_limit[event_type] = int(event_limit)
            updated_trigger_limit = triggers_limit
            values = {
                "updated_by": agent_id,
                "triggers_limit": json.dumps(updated_trigger_limit),
            }
            await EventRepository.update_event(app_name, event_name, values=values)

    @staticmethod
    async def common_validation_checks(
        app_name: Optional[str] = None,
        event_name: Optional[str] = None,
        event_id: Optional[int] = None,
    ):
        if not app_name:
            raise BadRequestException("app name is missing in the paylaod")
        check_format(app_name)    
        if not event_name:
            raise BadRequestException("event name is missing in the paylaod")
        check_format(event_name)    
        if not event_id:
            raise BadRequestException("event id is missing in the paylaod")

        data = await EventRepository.get_events_by_id(event_id)
        if not data:
            raise BadRequestException("no event is exists for the given event id")
        if data.event_name != event_name:
            raise BadRequestException(
                f"for the event id :{event_id} , event name is {data.event_name} .please enter the correct event name"
            )
        if data.app_name != app_name:
            raise BadRequestException(
                f"for the event id :{event_id} , app name is {data.app_name} .please enter the correct app name"
            )

        return data
