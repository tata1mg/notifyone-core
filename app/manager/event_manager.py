import logging
from typing import Optional
from app.constants import sms
from app.repositories.event import EventRepository
from app.manager.email_manager import EmailManager
from app.manager.sms_manager import SmsManager
from app.manager.push_notification_manager import PushManager
from app.manager.whatsapp_manager import WhatsappManager
from app.constants.constants import Event

logger = logging.getLogger()

class EventManager:

    @classmethod
    async def get_all_events(cls, event_id: Optional[int] = None, query_params: Optional[dict] = None):
        result_data = dict()
        all_templates = await EventRepository.get_all_templates(event_id, query_params)
        (
            email_templates,
            sms_templates,
            push_templates,
            whatsapp_templates,
        ) = cls.filter_all_templates(all_templates)

        if email_templates:
            email_templates = await EmailManager.filter_email(
                email_templates=email_templates, query_params=query_params
            )
            if email_templates.get('size'):
                email_templates.pop('size')
            if email_templates.get('start'):
                email_templates.pop('start')   
            result_data.update(email_templates)

        if sms_templates:
            sms_templates = await SmsManager.filter_sms(
                sms_templates=sms_templates, query_params=query_params
            )
            if sms_templates.get('size'):
                sms_templates.pop('size')
            if sms_templates.get('start'):
                sms_templates.pop('start')
            result_data.update(sms_templates)

        if push_templates:
            push_templates = await PushManager.filter_push_notification(
                push_templates=push_templates, query_params=query_params
            )
            if push_templates.get('size'):
                push_templates.pop('size')
            if push_templates.get('start'):
                push_templates.pop('start')
            result_data.update(push_templates)
        if whatsapp_templates:
            whatsapp_templates = await WhatsappManager.filter_whatsapp(
                whatsapp_templates=whatsapp_templates, query_params=query_params
            )
            if whatsapp_templates.get('size'):
                whatsapp_templates.pop('size')
            if whatsapp_templates.get('start'):
                whatsapp_templates.pop('start')
            result_data.update(whatsapp_templates)

        if not event_id and query_params and (not query_params.get('app_name') or not query_params.get('event_name')):
            result_data['start'] = query_params.get('start', Event.DEFAULT_OFFSET)
            result_data['size'] = query_params.get('size', Event.DEFAULT_LIMIT)   
        return result_data

    @classmethod
    def filter_all_templates(cls, data):
        email_templates = list()
        sms_templates = list()
        push_templates = list()
        whatsapp_templates = list()
        for item in data:
            template = {
                "event_id": item["event_id"],
                "event_name": item["event_event_name"],
                "app_name": item["event_app_name"],
                "actions": item["event_actions"],
                "triggers_limit": item["event_triggers_limit"],
            }

            if item["sms_id"] is not None:
                sms_template = {"id": item["sms_id"], "content": item["sms_content"]}
                sms_templates.append({**template, **sms_template})

            if item["email_id"] is not None:
                email_template = {
                    "id": item["email_id"],
                    "name": item["email_name"],
                    "description": item["email_description"],
                    "subject": item["email_subject"],
                    "content": item["email_content"],
                    "updated_by": item["email_updated_by"],
                }
                email_templates.append({**template, **email_template})

            if item["whatsapp_id"] is not None:
                whatsapp_template = {
                    "id": item["whatsapp_id"],
                    "name": item["whatsapp_name"],
                }
                whatsapp_templates.append({**template, **whatsapp_template})

            if item["push_id"] is not None:
                push_template = {
                    "id": item["push_id"],
                    "target": item["push_target"],
                    "body": item["push_body"],
                    "title": item["push_title"],
                    "image": item["push_image"],
                    "updated_by": item["push_updated_by"],
                    "updated": item["push_updated"],
                }
                push_templates.append({**template, **push_template})

        return email_templates, sms_templates, push_templates, whatsapp_templates
