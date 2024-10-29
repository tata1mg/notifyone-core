import logging
import json
from datetime import datetime
from typing import Optional, List, Dict
from torpedo.exceptions import BadRequestException
from app.repositories.push_notification import PushNotificationRepository
from app.constants.push import PushTarget
from app.constants.notification_channels import NotificationChannels
from app.utilities.utils import current_utc_timestamp
from app.repositories.generic_data_store import GenericDataRepository
from app.manager.generic_data_manager import GenericDataStoreManager
from app.utilities.drivers.jinja import CustomJinjaEnvironment
from app.manager.base_manager import BaseManager
from app.constants.constants import Event
from app.constants.push import Push
from app.constants.error_messages import ErrorMessages
from app.exceptions import NotFoundException,RequiredParamsException

logger = logging.getLogger()

class PushManager(BaseManager):

    @classmethod
    async def filter_push_notification(
        cls,
        event_id: Optional[int] = None,
        query_params: Optional[Dict] = None,
        push_templates: Optional[List] = None,
    ):
        if not push_templates:
            push_templates = (
                await PushNotificationRepository.get_push_notification_templates(
                    event_id, query_params
                )
            )
        filtered_notifications = [
            await cls._filter_push_notification(push_notification)
            for push_notification in push_templates
        ]

        if event_id:
            filtered_notifications = filtered_notifications[0]

        result = {"push": filtered_notifications}

        if not event_id and query_params and (not query_params.get('app_name') or not query_params.get('event_name')):
            result['start'] = query_params.get('start', Event.DEFAULT_OFFSET)
            result['size'] = query_params.get('size', Event.DEFAULT_LIMIT)    
        return result

    @classmethod
    async def _filter_push_notification(cls, push_notification: Dict):
        filtered_notification = dict()
        if push_notification:
            keys_required = [
                "event_id",
                "event_name",
                "app_name",
                "actions",
                "triggers_limit",
                "id",
                "title",
                "body",
                "target",
                "image",
                "updated_by",
                "updated",
            ]
            for key, value in push_notification.items():
                if key in keys_required:
                    if key in ["actions", "triggers_limit"]:
                        value = json.loads(value)
                        filtered_notification[key] = value["push"]
                    else:
                        filtered_notification[key] = value

            if filtered_notification.get("updated"):
                filtered_notification["updated"] = filtered_notification.get(
                    "updated"
                ).strftime("%s")

            if filtered_notification.get("target"):
                filtered_notification["target"] = cls.get_target_type_by_target(
                    filtered_notification["target"]
                )

            if filtered_notification.get("event_id"):
                generic_data = await GenericDataRepository.get_data_store_entry(
                    filtered_notification.get("event_id"), category="event_body"
                )
                if generic_data:
                    filtered_notification["data"] = generic_data.data
                else:
                    filtered_notification["data"] = dict()
        return filtered_notification

    @classmethod
    def get_target_type_by_target(cls, target: str):
        # Handling dynamic target (used by labs). We just jinjafy the target here
        if target == PushTarget.DYNAMIC_TARGET["value"]:
            return PushTarget.DYNAMIC_TARGET["name"]
        for target_type in cls.get_all_target_types():
            if target == cls.get_push_target(target_type):
                return target_type
        return None

    @classmethod
    def get_all_target_types(cls):
        return list(PushTarget.TARGET.keys())

    @classmethod
    def get_push_target(cls, target_type: str):
        if not target_type:
            return ""
        # Handling dynamic target (used by labs). We just jinjafy the target here
        if target_type == PushTarget.DYNAMIC_TARGET["name"]:
            return PushTarget.DYNAMIC_TARGET["value"]
        target_type = target_type.upper()
        if target_type.upper() not in cls.get_all_target_types():
            raise Exception("Target name does not exists")
        url_separator = "://"
        query_params_start = "?"
        target_details = PushTarget.TARGET[target_type]
        target = (
            target_details["PROTOCOL"]
            + url_separator
            + target_details["DOMAIN_NAME"]
            + target_details["URL"]
        )
        if target_details.get("query_params"):
            query_params_array = []
            for query_param in target_details["query_params"]:
                query_param_string = query_param["name"] + "="
                if query_param.get("place_holder"):
                    query_param_string += "{{" + query_param["place_holder"] + "}}"
                elif query_param.get("direct_value"):
                    query_param_string += query_param["direct_value"]
                query_params_array.append(query_param_string)
            query_params_string = "&".join(query_params_array)
            target += query_params_start + query_params_string
        return target

    @classmethod
    async def update_push_notification(cls, push_id, data, agent_id, **kwargs):
        if kwargs["payload"].get("title") is None:
            raise BadRequestException("title is missing in the payload")

        if kwargs["payload"].get("body") is None:
            raise BadRequestException("body is missing in the payload")

        to_update = {
            "title": kwargs["payload"].get("title"),
            "body": kwargs["payload"].get("body"),
            "updated_by": agent_id,
        }
        if kwargs["payload"].get("image"):
            to_update.update({"image": kwargs["payload"].get("image")})

        if "target" in kwargs["payload"]:
            to_update["target"] = cls.get_push_target(kwargs["payload"]["target"])

        to_update["updated"] = current_utc_timestamp()
        await cls.update_trigger_limit(
            NotificationChannels.PUSH.value, agent_id, **kwargs
        )
        await PushNotificationRepository.update_push_notification(
            notification_id=push_id, to_update=to_update
        )
        event_id = kwargs["payload"].get("event_id")
        await GenericDataStoreManager.update_or_insert_data_store_entry(
                event_id, data, agent_id
            )

    @staticmethod
    async def get_push_template_previews(event_id, body, title, data):
        template = await PushNotificationRepository.get_push_notification(event_id)
        if not template:
            raise BadRequestException("template is not exists. please verify the event id ")
        if not body:
            raise BadRequestException("content body is missing in the paylaod")
        if not title:
            raise BadRequestException("content title is missing in the paylaod")

        body = CustomJinjaEnvironment.render_text(body, data)
        title = CustomJinjaEnvironment.render_text(title, data)
        return {"body": body, "title": title}

class CreatePushEvent:
    """
    Class for creating new push events or adding its action in the existing event.
    """
    @classmethod
    def prepare_event_actions(cls, data: Dict):
        """
        This function is used to prepare push action in dict for event .
        :param data: dict containing different event's field.
        :param actions : dict of actions to be added in events
        :return: dict
        """
        actions = {}
        actions[NotificationChannels.PUSH.value] = data.get(
            NotificationChannels.PUSH.value
        )
        return actions

    @classmethod
    async def get_data_for_event(
        cls, data: Dict, user_email: str, event_id: Optional[int] = None
    ):
        """
        This function is used to get push data for event .
        :param data: dict containing  push's field.
        :param user_email: str email of the user
        :return: None
        """
        push_title = data.get(Push.TITLE)
        if not push_title:
            raise RequiredParamsException(
                ErrorMessages.REQUIRED_FIELD.value.format(
                    NotificationChannels.PUSH.value, Push.TITLE
                )
            )
        push_body = data.get(Push.BODY)
        if not push_body:
            raise RequiredParamsException(
                ErrorMessages.REQUIRED_FIELD.value.format(
                    NotificationChannels.PUSH.value, Push.BODY
                )
            )
        push = {
            "title": push_title,
            "body": push_body,
            "target": data.get("target", ""),
            "image": data.get("image", ""),
            "device_type": data.get(
                "device_type", "ALL"
            ),  # NOTE: by default device_type will be ALL
            "device_version": data.get("device_version", ""),
            "updated_by": user_email,
        }
        if event_id:
            push_data_db = await PushNotificationRepository.get_push_notification(
                event_id
            )
            if push_data_db:
                raise BadRequestException(
                    ErrorMessages.ACTION_ALREADY_ADDED_ERROR.value.format(
                        NotificationChannels.PUSH.value
                    )
                )

        return push

    @classmethod
    async def create_post_event_entry(cls, push, event_id):
        """
        This is used to create push_notification entry
        :param  push: dict containing email data
        :param event_id: id of the event.
        :return: None
        """
        if not push:
            raise NotFoundException(
                ErrorMessages.PUSH_DATA_NOT_FOUND_ERROR.value
            )
        push["event_id"] = event_id
        await PushNotificationRepository.create_push_notification_entry(push=push)
