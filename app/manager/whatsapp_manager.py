import logging
import json
from typing import Optional, Dict, List
from torpedo.exceptions import BadRequestException
from app.repositories.whatsapp_content import WhatsappContentRepository
from app.constants.notification_channels import NotificationChannels
from app.utilities.utils import current_utc_timestamp
from app.manager.base_manager import BaseManager
from app.constants.constants import Event
from app.constants.whatsapp import  Whatsapp
from app.exceptions import NotFoundException, RequiredParamsException
from app.constants.error_messages import ErrorMessages

logger = logging.getLogger()

class WhatsappManager(BaseManager):

    @classmethod
    async def filter_whatsapp(
        cls,
        event_id: Optional[int] = None,
        query_params: Optional[Dict] = None,
        whatsapp_templates: Optional[List] = None,
    ):
        if not whatsapp_templates:
            whatsapp_templates = await WhatsappContentRepository.get_whatsapp_templates(
                event_id, query_params
            )
        filtered_whatsapp_templates = [
            await cls.filter_whatsapp_templates(whatsapp_template)
            for whatsapp_template in whatsapp_templates
        ]

        result = {"whatsapp": filtered_whatsapp_templates[0]} if len(filtered_whatsapp_templates) == 1 else {"whatsapp": filtered_whatsapp_templates}

        if not event_id and query_params and (not query_params.get('app_name') or not query_params.get('event_name')):
            result['start'] = query_params.get('start', Event.DEFAULT_OFFSET)
            result['size'] = query_params.get('size', Event.DEFAULT_LIMIT)     
        return result
        
    @classmethod
    async def filter_whatsapp_templates(cls, whatsapp_template: Dict):
        filtered_whatsapp_templates = dict()
        if whatsapp_template:
            keys_required = [
                "event_name",
                "app_name",
                "actions",
                "triggers_limit",
                "id",
                "name",
                "event_id",
            ]
            for key, value in whatsapp_template.items():
                if key in keys_required:
                    if key in ["actions", "triggers_limit"]:
                        value = json.loads(value)
                        filtered_whatsapp_templates[key] = value["whatsapp"]
                    else:
                        filtered_whatsapp_templates[key] = value
        return filtered_whatsapp_templates

    @classmethod
    async def update_whatsapp_table(cls, whatsapp_template_id, agent_id, **kwargs):
        if kwargs["payload"].get("name") is None:
            raise BadRequestException("name is missing in the payload")
            
        to_update = {"name": kwargs["payload"].get("name"), "updated_by": agent_id}
        await cls.update_trigger_limit(
            NotificationChannels.WHATSAPP.value, agent_id, **kwargs
        )
        to_update["updated"] = current_utc_timestamp()
        await WhatsappContentRepository.update_whatsapp_table(
            whatsapp_template_id=whatsapp_template_id, to_update=to_update
        )

class CreateWhatsappEvent:
    """
    Class for creating new whatsapp events or adding its action in the existing event.
    """
    @classmethod
    def prepare_event_actions(cls, data: Dict):
        """
        This function is used to prepare whatsapp action in dict for event .
        :param data: dict containing different event's field.
        :param actions : dict of actions to be added in events
        :return: dict
        """
        actions = {}
        actions[NotificationChannels.WHATSAPP.value] = data.get(
            NotificationChannels.WHATSAPP.value
        )
        return actions

    @classmethod
    async def get_data_for_event(
        cls, data: Dict, user_email: str, event_id: Optional[int] = None
    ):
        """
        This function is used to get data for event .
        :param data: dict containing sms's field.
        :param user_email: str email of the user
        :return: dict
        """
        name = data.get(Whatsapp.NAME)
        if not name:
            raise RequiredParamsException(
                ErrorMessages.REQUIRED_FIELD.value.format(
                    NotificationChannels.WHATSAPP.value, Whatsapp.NAME
                )
            )
        whatsapp = {"name": name, "updated_by": user_email}
        if event_id:
            whatsapp_data_db = (
                await WhatsappContentRepository.get_whatsapp_content_from_event_id(
                    event_id
                )
            )
            if whatsapp_data_db:
                raise BadRequestException(
                    ErrorMessages.ACTION_ALREADY_ADDED_ERROR.value.format(
                        NotificationChannels.WHATSAPP.value
                    )
                )
        return whatsapp

    @classmethod
    async def create_post_event_entry(cls, whatsapp, event_id):
        """
        This is used to create push_notification entry
        :param whatsapp: dict containing email data
        :param event_id: id of the event.
        :return: None
        """
        if not whatsapp:
            raise NotFoundException(
                ErrorMessages.WHATSAPP_DATA_NOT_FOUND_ERROR.value
            )
        whatsapp["event_id"] = event_id
        await WhatsappContentRepository.create_whatsapp_entry(whatsapp=whatsapp)
