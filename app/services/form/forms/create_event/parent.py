from app.constants import EventPriority, EventType
from app.services.apps import AppService
from app.services.form.fields import (
    Collection,
    SelectField,
    TextInput,
    Option,
    SwtichField,
)
from app.services.form import GenericForm
from app.services.form.fields.field_rule import Required

from .email import EmailForm
from .sms import SmsForm
from .push import PushForm
from .whatsapp import WhatsAppForm


class CreateEventForm(GenericForm):
    @classmethod
    async def __get_app_name_options(cls):
        app_names = []
        names = await AppService.list_app_names()
        for name in names:
            app_names.append(Option(value=name, label=name))
        return app_names

    @classmethod
    async def _get_components(cls):
        return {
            "app_name": SelectField(
                name="app_name",
                label="App Name",
                options=await cls.__get_app_name_options(),
                showSearch=True,
                rules=[Required],
            ),
            "event_name": TextInput(
                name="event_name", label="Event Name", rules=[Required]
            ),
            "event_type": SelectField(
                name="event_type",
                label="Event Type",
                options=Option.from_enum(EventType),
                rules=[Required],
            ),
            "callback_enabled": SwtichField(
                name="callback_enabled",
                label="Callback Enabled",
                span=12,
            ),
            "priority": SelectField(
                name="priority",
                label="Priority",
                span=12,
                options=Option.from_enum(EventPriority),
                rules=[Required],
            ),
            "email": EmailForm.get(),
            "sms": SmsForm.get(),
            "push": PushForm.get(),
            "whatsapp": WhatsAppForm.get(),
        }

    @classmethod
    async def get(cls):
        components = await cls._get_components()
        return Collection(
            name="create_event",
            label="Create Event",
            order=[
                "app_name",
                "event_name",
                "event_type",
                "callback_enabled",
                "priority",
                "email",
                "sms",
                "push",
                "whatsapp",
            ],
            components=components,
        )
