from app.constants.callbacks import (
    EmailEventStatus,
    SmsEventStatus,
    PushEventStatus,
    WhatsAppEventStatus,
)
from app.services.form.enums import SelectMode
from app.services.form.fields import (
    Collection,
    Option,
    SelectField,
    TextInput,
    UrlInput,
    EmailInput,
)
from app.services.form import GenericForm
from app.services.form.fields.field_rule import Required


class CreateAppForm(GenericForm):

    @classmethod
    async def __get_metadata_components(cls) -> dict:
        return {
            "sender_details": Collection(
                name="sender_details",
                label="Sender Details",
                order=["email"],
                components=await cls.__get_sender_details_components()
            )
        }

    @classmethod
    async def __get_sender_details_components(cls) -> dict:
        return {
            "email": Collection(
                name="email",
                label="Email Sender Details",
                order=["name", "address", "reply_to"],
                components=await cls.__get_email_sender_components()
            )
        }

    @classmethod
    async def __get_email_sender_components(cls) -> dict:
        return {
            "name": TextInput(name="name", label="Email Sender Name"),
            "address": EmailInput(name="address", label="Email Sender Address"),
            "reply_to": EmailInput(name="reply_to", label="Reply To Address")
        }

    @classmethod
    async def __get_callback_events_components(cls):
        return {
            "email": SelectField(
                name="email",
                label="Email",
                mode=SelectMode.MULTIPLE,
                options=Option.from_enum(EmailEventStatus),
            ),
            "sms": SelectField(
                name="sms",
                label="SMS",
                mode=SelectMode.MULTIPLE,
                options=Option.from_enum(SmsEventStatus),
            ),
            "push": SelectField(
                name="push",
                label="Push",
                mode=SelectMode.MULTIPLE,
                options=Option.from_enum(PushEventStatus),
            ),
            "whatsapp": SelectField(
                name="whatsapp",
                label="WhatsApp",
                mode=SelectMode.MULTIPLE,
                options=Option.from_enum(WhatsAppEventStatus),
            ),
        }

    @classmethod
    async def _get_components(cls):
        return {
            "name": TextInput(name="name", label="Name", rules=[Required]),
            "callback_url": UrlInput(name="callback_url", label="Callback URL"),
            "callback_events": Collection(
                name="callback_events",
                label="Callback Events",
                order=["email", "sms", "push", "whatsapp"],
                components=await cls.__get_callback_events_components(),
            ),
            "metadata": Collection(
                name="metadata",
                label="Meta Data",
                order=["sender_details"],
                components=await cls.__get_metadata_components()
            )
        }

    @classmethod
    async def get(cls):
        components = await cls._get_components()
        return Collection(
            name="create_app",
            label="Create App",
            order=[
                "name",
                "callback_url",
                "callback_events",
                "metadata"
            ],
            components=components,
        )
