import logging
import json
from typing import List, Optional, Dict
from torpedo.exceptions import BadRequestException
from app.repositories.event import EventRepository
from app.repositories.sms_content import SmsContentRepository
from app.repositories.generic_data_store import GenericDataRepository
from app.constants.notification_channels import NotificationChannels
from app.constants.sms import EventName
from app.manager.generic_data_manager import GenericDataStoreManager
from app.manager.base_manager import BaseManager
from app.utilities import get_transformed_message_by_text, current_utc_timestamp, check_format
from app.constants.constants import Event
from app.constants.sms import Sms
from app.constants.error_messages import ErrorMessages
from app.exceptions import RequiredParamsException, NotFoundException

logger = logging.getLogger()

class SmsManager(BaseManager):

    @classmethod
    async def filter_sms(
        cls,
        event_id: Optional[int] = None,
        query_params: Optional[Dict] = None,
        sms_templates: Optional[List] = None,
    ):
        if not sms_templates:
            sms_templates = await SmsContentRepository.get_sms_templates(
                event_id, query_params
            )
        filtered_sms_templates = [
            await cls._filter_sms_templates(sms_template)
            for sms_template in sms_templates
        ]
        result = {"sms": filtered_sms_templates[0]} if len(filtered_sms_templates) == 1 else {"sms": filtered_sms_templates}

        if not event_id and query_params and (not query_params.get('app_name') or not query_params.get('event_name')):
            result['start'] = query_params.get('start', Event.DEFAULT_OFFSET)
            result['size'] = query_params.get('size', Event.DEFAULT_LIMIT)     
        return result

    @classmethod
    async def _filter_sms_templates(cls, sms_templates: Dict):
        filtered_sms_templates = dict()
        if sms_templates:
            keys_required = [
                "event_name",
                "app_name",
                "actions",
                "triggers_limit",
                "id",
                "content",
                "event_id",
            ]
            for key, value in sms_templates.items():
                if key in keys_required:
                    if key in ["actions", "triggers_limit"]:
                        value = json.loads(value)
                        filtered_sms_templates[key] = value["sms"]
                    else:
                        filtered_sms_templates[key] = value
        if sms_templates.get("event_id"):
            generic_data = await GenericDataRepository.get_data_store_entry(
                sms_templates.get("event_id"), category="event_body"
            )
            if generic_data:
                filtered_sms_templates["data"] = generic_data.data
            else:
                filtered_sms_templates["data"] = dict()
        return filtered_sms_templates

    @classmethod
    async def update_sms_template(cls, sms_id, data, agent_id, **kwargs):
        if kwargs["payload"].get("content") is None:
            raise BadRequestException("content is missing in the paylaod")
        to_update = {
            "content": kwargs["payload"].get("content"),
            "updated_by": agent_id,
        }
        await cls.update_trigger_limit(
            NotificationChannels.SMS.value, agent_id, **kwargs
        )
        to_update["updated"] = current_utc_timestamp()
        await SmsContentRepository.update_sms_template(
            sms_id=sms_id, to_update=to_update
        )
        event_id = kwargs["payload"].get("event_id")
        await GenericDataStoreManager.update_or_insert_data_store_entry(
                event_id, data, agent_id
            )

    @staticmethod
    async def get_sms_template_previews(content, event_name, user_email, data):
        """
        This function will return preview body for a template (SMS and email)
        :param event_name:
        :param application_name:
        :param email:
        :param template:
        :param event_type:
        :return:
        """ 
        if content is None:
            raise BadRequestException("content is missing in the paylaod")
        if event_name is None:
            raise BadRequestException("event name is missing in the paylaod")
        check_format(event_name)
        result = await EventRepository.get_event_details(event_name=event_name)
        if not result:
            raise BadRequestException("event name is not exists. please verify the event name")      
        if event_name in EventName.get_all_event_name():
            return content
        event_body = data
        meta_data_for_preview = dict()
        meta_data_for_preview["to"] = user_email
        meta_data_for_preview["body"] = dict()
        if "order" in event_body:
            meta_data_for_preview["body"]["order"] = event_body["order"]
            del event_body["order"]
        meta_data_for_preview["body"].update(event_body)
        body = await get_transformed_message_by_text(
            content, meta_data_for_preview["body"]
        )
        return body.replace("\n", "")

class CreateSmsEvent:
    """
    Class for creating new sms events or adding its action in the existing event.
    """
    @classmethod
    def prepare_event_actions(cls, data: Dict):
        """
        This function is used to prepare sms action in dict for event .
        :param data: dict containing different event's field.
        :param actions : dict of actions to be added in events
        :return: dict
        """
        actions = {}
        actions[NotificationChannels.SMS.value] = data.get(
            NotificationChannels.SMS.value
        )
        return actions

    @classmethod
    async def get_data_for_event(
        cls, data: Dict, user_email: str, event_id: Optional[int] = None
    ):
        """
        This function is used to get sms data for event .
        :param data: dict containing sms's field.
        :param user_email: str email of the user
        :return: dict
        """
        sms_content = data.get(Sms.CONTENT)
        if not sms_content:
            raise RequiredParamsException(
                ErrorMessages.REQUIRED_FIELD.value.format(
                    NotificationChannels.SMS.value, Sms.CONTENT
                )
            )
        sms = {"content": sms_content, "updated_by": user_email}
        if event_id:
            sms_data_db = await SmsContentRepository.get_sms_content_from_event_id(
                event_id
            )
            if sms_data_db:
                raise BadRequestException(
                    ErrorMessages.ACTION_ALREADY_ADDED_ERROR.value.format(
                        NotificationChannels.SMS.value
                    )
                )

        return sms

    @classmethod
    async def create_post_event_entry(cls, sms, event_id):
        """
        This is used to create sms entry
        :param sms: dict containing sms data
        :param event_id: id of the event.
        :return: None
        """
        if not sms:
            raise NotFoundException(
                ErrorMessages.SMS_DATA_NOT_FOUND_ERROR.value
            )
        sms["event_id"] = event_id
        await SmsContentRepository.create_sms_entry(sms=sms)
        