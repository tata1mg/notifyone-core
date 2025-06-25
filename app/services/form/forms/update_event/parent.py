from torpedo.exceptions import NotFoundException
from app.repositories.event import EventRepository
from app.constants.event import EventType
from app.models.notification_core import EventModel
from app.repositories.email_content import EmailContentRepository
from app.repositories.sms_content import SmsContentRepository
from app.repositories.push_notification import PushNotificationRepository
from app.repositories.whatsapp_content import WhatsappContentRepository

from app.services.form.fields import (
    Collection,
    SelectField,
    TextInput,
    SwtichField,
    Option,
)
from app.services.form.fields.field_rule import Required
from app.utilities.utils import async_gather_dict
from app.services.form import GenericForm


from .email import EmailForm
from .sms import SmsForm
from .push import PushForm
from .whatsapp import WhatsAppForm
from .default_content import NoneEmailContentModel, NoneSmsContentModel, NonePushContentModel, NoneWhatsappContentModel


class UpdateEventForm(GenericForm):
    def __init__(self, event_id) -> None:
        self._event_id = event_id

    async def get_channel_content(self, event_id):
        tasks = {
            "email": EmailContentRepository.get_email_content_from_event_id(event_id),
            "sms": SmsContentRepository.get_sms_content_from_event_id(event_id),
            "push": PushNotificationRepository.get_push_notification(event_id),
            "whatsapp": WhatsappContentRepository.get_whatsapp_content_from_event_id(event_id)
        }
        result = await async_gather_dict(tasks, return_exceptions=True)
        return {
            "email": result.get("email") if result.get("email") else NoneEmailContentModel,
            "sms": result.get("sms") if result.get("sms") else NoneSmsContentModel,
            "push": result.get("push") if result.get("push") else NonePushContentModel,
            "whatsapp": result.get("whatsapp") if result.get("whatsapp") else NoneWhatsappContentModel,
        }

    async def _get_components(self, event: EventModel, event_contents: dict):
        component = {
            "app_name": SelectField(
                name="app_name",
                label="App Name",
                initialValue=event.app_name,
                disabled=True,
                rules=[Required],
            ),
            "event_name": TextInput(
                name="event_name", label="Event Name", initialValue=event.event_name, disabled=True, rules=[Required]
            ),
            "event_type": SelectField(
                name="event_type",
                label="Event Type",
                initialValue=event.event_type,
                options=Option.from_enum(EventType),
                rules=[Required],
            ),
            "callback_enabled": SwtichField(
                name="callback_enabled",
                label="Callback Enabled",
                initialValue=event.callback_enabled,
                span=12,
            ),
            "dynamic_channels": SwtichField(
                name="dynamic_channels",
                label="Dynamic Channels",
                initialValue=event.dynamic_channel_allowed,
                span=12,
            ),
            "priority": SelectField(
                name="priority",
                label="Priority",
                initialValue=event.priority,
                span=12,
                disabled=True,
                rules=[Required],
            ),
            "email": EmailForm(event_contents.get("email"), event.triggers_limit.get("email"), event.actions.get("email")).get(),
            "sms": SmsForm(event_contents.get("sms"), event.triggers_limit.get("sms"), event.actions.get("sms")).get(),
            "push": PushForm(event_contents.get("push"), event.triggers_limit.get("push"), event.actions.get("push")).get(),
            "whatsapp": WhatsAppForm(event_contents.get("whatsapp"), event.triggers_limit.get("whatsapp"), event.actions.get("whatsapp")).get(),
        }
        return component
    
    async def get(self):
        event = await EventRepository.get_events_by_id(self._event_id)
        if not event:
            raise NotFoundException(f"no event found for event id : {self._event_id}")
        event_contents = await self.get_channel_content(self._event_id)
        components = await self._get_components(event, event_contents)
        return Collection(
            name="update_event",
            label="Update Event",
            order=[
                "app_name",
                "event_name",
                "event_type",
                "callback_enabled",
                "dynamic_channels",
                "priority",
                "email",
                "sms",
                "push",
                "whatsapp",
            ],
            components=components,
        )