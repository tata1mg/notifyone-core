import logging
import json
import asyncio
from re import template
from typing import List, Optional, Dict
from torpedo.exceptions import BadRequestException
from app.constants.notification_channels import NotificationChannels
from app.constants.email import Email
from app.repositories.email_content import EmailContentRepository
from app.exceptions import NotFoundException, RequiredParamsException
from app.caches.notification_core_cache import CacheHelper
from app.utilities.utils import (
    current_epoch_in_millis,
    current_utc_timestamp,
   get_event_unique_identifier,
    get_email_content_path,
)
from app.services.email import EmailHandler
from app.utilities.drivers.jinja import CustomJinjaEnvironment
from app.manager.generic_data_manager import GenericDataStoreManager
from app.repositories.generic_data_store import GenericDataRepository
from app.constants.error_messages import ErrorMessages
from app.models.notification_core.email_content import EmailContentModel
from app.manager.base_manager import BaseManager
from app.constants.constants import Event

logger = logging.getLogger()

class EmailManager(BaseManager):

    @classmethod
    async def filter_email(
        cls,
        event_id: Optional[int] = None,
        query_params: Optional[Dict] = None,
        email_templates: Optional[List] = None,
    ):
        if not email_templates:
            email_templates = await EmailContentRepository.get_email_templates(
                event_id, query_params
            )
        filtered_email_templates = [
            await cls._filtered_email_templates(email_template)
            for email_template in email_templates
        ]

        if event_id:
            filtered_email_templates = filtered_email_templates[0]

        result = {"email": filtered_email_templates}

        if not event_id and query_params and (not query_params.get('app_name') or not query_params.get('event_name')):
            result['start'] = query_params.get('start', Event.DEFAULT_OFFSET)
            result['size'] = query_params.get('size', Event.DEFAULT_LIMIT)
        return result 

    @classmethod
    async def _filtered_email_templates(cls, email_template: Dict):

        filtered_email_template = dict()
        if email_template:
            keys_required = [
                "id",
                "name",
                "description",
                "subject",
                "content",
                "updated_by",
                "event_id",
                "event_name",
                "app_name",
                "actions",
                "triggers_limit",
            ]
            for key, value in email_template.items():

                if key in keys_required:
                    if key in ["actions", "triggers_limit"]:
                        value = json.loads(value)
                        filtered_email_template[key] = value["email"]
                    else:
                        filtered_email_template[key] = value

            if email_template.get("content"):
                filtered_email_template[
                    "includes"
                ] = await cls.get_includes_in_template(
                    email_template["content"], add_template_name=True
                )

            if email_template.get("event_id"):
                generic_data = await GenericDataRepository.get_data_store_entry(
                    email_template.get("event_id"), category="event_body"
                )

                if generic_data:
                    filtered_email_template["data"] = generic_data.data
                else:
                    filtered_email_template["data"] = dict()

        return filtered_email_template

    @classmethod
    async def get_includes_in_template(
        cls, template_content: str, add_template_name: Optional[bool] = None
    ):
        includes = []
        if cls.is_content_html(template_content):
            return includes
        for line in template_content.splitlines():
            striped_line = line.strip()
            if striped_line.startswith(Email.INCLUDE_START) and striped_line.endswith(
                Email.INCLUDE_END
            ):
                start, end = len(Email.INCLUDE_START), striped_line.index(
                    Email.INCLUDE_END
                )
                unique_identifier = int(striped_line[start:end].strip())
                name = "{}{}{}".format(
                    Email.INCLUDE_START, unique_identifier, Email.INCLUDE_END
                )
                if add_template_name:
                    template = (
                        await EmailContentRepository.get_email_content_from_template_id(
                            unique_identifier
                        )
                    )
                    if template:
                        template_name = template.name
                        name = "{}{}{}".format(unique_identifier, "-", template_name)
                include_content = {"id": unique_identifier, "name": name}
                includes.append(include_content)
        return includes

    @classmethod
    def is_content_html(cls, content: str):
        content = content or ""
        return "<html" in content

    @classmethod
    async def update_email_template(cls, id, updated_by, data, **kwargs):
        if kwargs["payload"].get("subject") is None:
            raise BadRequestException("subject is missing in the paylaod")

        if kwargs["payload"].get("content") is None:
            raise BadRequestException("content is missing in the paylaod")

        to_update = {
            "subject": kwargs["payload"].get("subject"),
            "content": kwargs["payload"].get("content"),
            "updated_by": updated_by,
        }
        if kwargs["payload"].get("description"):
            to_update.update({"description": kwargs["payload"].get("description")})

        if kwargs["payload"].get("name"):
            to_update.update({"name": kwargs["payload"].get("name")})

        template_ids_affected = await CacheHelper.get_preview_cache(
            user_id=updated_by, template_id=id
        )
        if not template_ids_affected:
            raise NotFoundException(
                "Run Preview Again"
            )
        await cls.update_trigger_limit(
            NotificationChannels.EMAIL.value, updated_by, **kwargs
        )
        to_update["updated"] = current_utc_timestamp()
        await EmailContentRepository.update_email_content(
            template_id=id, to_update=to_update
        )
        event_id = kwargs["payload"].get("event_id")
        await GenericDataStoreManager.update_or_insert_data_store_entry(
            event_id, data, updated_by
        )
        await cls.update_template_db_files(template_ids_affected)
        await EmailHandler.handle_email_template_update(
            latest_template_version=current_epoch_in_millis()
        )
        return {"message": "email template updated successfully"}

    @classmethod
    async def update_template_db_files(cls, template_ids: List):
        templates_details = (
            await EmailContentRepository.get_email_content_from_template_ids(
                template_ids
            )
        )
        for template_details in templates_details:
            template_detail = template_details
            event_id = template_detail.event_id
            event_data = await GenericDataStoreManager.get_event_body(event_id)
            await EmailHandler.get_email_body_from_template_content(
                template_detail, event_data
            )

    @classmethod
    async def get_email_template_previews(
        cls,
        subject: str,
        content: str,
        template_id: str,
        send_email_to: str,
        data: Optional[Dict] = None,
    ):
        if subject is None:
            raise BadRequestException("Subject is missing in the payload template")

        if content is None:
            raise BadRequestException("Content is missing in the payload template")

        template_details = (
            await EmailContentRepository.get_email_content_from_template_id(
                id=template_id
            )
        )
        if not template_details:
            raise NotFoundException(
                "Template doesn't exist"
            )
        template_ids_affected = set()
        all_non_event_template_details = await EmailHandler.get_all_email_content_map()
        if template_details.event_id:
            template_ids_affected.add(template_details.id)
            template_details.content = content
            template_details.subject = subject
            template, subject = await cls.get_template_content(
                template_details,
                all_non_event_template_details,
                "preview",
                send_email_to,
                data,
            )
            final_result = {"previews": {"content": template, "subject": subject}}
        else:
            result = []
            all_non_event_template_details[int(template_id)] = content
            all_events = await EmailHandler.get_all_dependent_events(template_id)
            if not all_events:
                raise NotFoundException(
                    "No email found"
                )
            for template_id in all_events:
                template_details = (
                    await EmailContentRepository.get_email_content_from_template_id(
                        template_id
                    )
                )
                template_ids_affected.add(template_details.id)
                template, subject = await cls.get_template_content(
                    template_details,
                    all_non_event_template_details,
                    "preview",
                    data=data,
                )
                # yet to implement this part for send emails
                result.append({"content": template, "subject": subject})
            final_result = {"previews": result}
        await CacheHelper.create_preview_cache(
            send_email_to, template_id, list(template_ids_affected)
        )
        return final_result

    @classmethod
    async def get_template_content(
        cls,
        template_details: EmailContentModel,
        email_content_map: Dict,
        request_type: str,
        send_email_to: Optional[str] = None,
        data: Optional[Dict] = None,
    ):
        event_id = template_details.event_id
        if data is None:
            data = await GenericDataStoreManager.get_event_body(event_id)
        if not data:
            raise NotFoundException(
                "Event data is not prepared"
            )
        template = await EmailHandler.get_email_content(
            template_details, email_content_map, data, request_type, send_email_to
        )
        subject = template_details.subject or Email.SUBJECT
        subject = CustomJinjaEnvironment.render_text(subject, data)
        if send_email_to:
            pass
            # data = dict()
            # await EmailHandler.publish(data, send_email_to, subject, template)
        return template, subject

    @classmethod
    async def include_email_template(
        cls, name, content, description, subject, user_email
    ):
        if not name:
            raise RequiredParamsException(
                ErrorMessages.REQUIRED_FIELD.value.format(
                    NotificationChannels.EMAIL.value, Email.NAME
                )
            )
        if not content:
            raise RequiredParamsException(
                ErrorMessages.REQUIRED_FIELD.value.format(
                    NotificationChannels.EMAIL.value, Email.CONTENT
                )
            )

        subject = subject or Email.SUBJECT
        description = description or Email.DESCRIPTION
        unique_identifier = name
        path = get_email_content_path(unique_identifier)
        email = {
            "description": description,
            "subject": subject,
            "content": content,
            "name": unique_identifier,
            "path": path,
            "updated_by": user_email,
        }
        result = await EmailContentRepository.create_email_entry(email)
        response = {
            "id": result.id,
            "name": result.name,
            "path": result.path,
            "content": result.content,
            "subject": result.subject,
            "updated_by": user_email,
        }
        return response

class CreateEmailEvent:
    """
    Class for creating new Email events or adding its action in the existing event.
    """
    @classmethod
    def prepare_event_actions(cls, data: Dict):
        """
        This function is used to prepare email action in dict for event .
        :param data: dict containing different event's field.
        :param actions : dict of actions to be added in events
        :return: dict
        """
        actions = {}
        actions[NotificationChannels.EMAIL.value] = data.get(
            NotificationChannels.EMAIL.value
        )
        return actions

    @classmethod
    async def get_data_for_event(
        cls,
        data: Dict,
        app_name: str,
        event_name: str,
        user_email: str,
        event_id: Optional[int] = None,
    ):
        """
        This function is used to get email data for event .
        :param data: dict containing email fields.
        :return: dict
        """
        subject = data.get(Email.SUBJECT)
        if not subject:
            raise RequiredParamsException(
                ErrorMessages.REQUIRED_FIELD.value.format(
                    NotificationChannels.EMAIL.value, Email.SUBJECT
                )
            )

        content = data.get(Email.CONTENT)
        if not content:
            raise RequiredParamsException(
                ErrorMessages.REQUIRED_FIELD.value.format(
                    NotificationChannels.EMAIL.value, Email.CONTENT
                )
            )

        description = data.get(Email.DESCRIPTION, "")
        unique_identifier = get_event_unique_identifier(event_name, app_name)
        path = get_email_content_path(unique_identifier)
        email = {
            "subject": subject,
            "description": description,
            "content": content,
            "name": unique_identifier,
            "path": path,
            "updated_by": user_email,
        }
        if event_id:
            email_data_db = (
                await EmailContentRepository.get_email_content_from_event_id(event_id)
            )
            if email_data_db:
                raise BadRequestException(
                    ErrorMessages.ACTION_ALREADY_ADDED_ERROR.value.format(
                        NotificationChannels.EMAIL.value
                    )
                )
        return email

    @classmethod
    async def create_post_event_entry(cls, email, event_id):
        """
        This is used to create email entry
        :param email: dict containing email data
        :param event_id: id of the event.
        :return: None
        """
        if not email:
            raise NotFoundException(
                ErrorMessages.EMAIL_DATA_NOT_FOUND_ERROR.value
            )
        email["event_id"] = event_id
        await EmailContentRepository.create_email_entry(email=email)
