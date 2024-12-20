from app.constants.callbacks import (
    EmailEventStatus,
    SmsEventStatus,
    PushEventStatus,
    WhatsAppEventStatus,
)
from app.models.notification_core import AppsModel
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
from app.repositories.apps import AppsRepository


class UpdateAppForm(GenericForm):

    @classmethod
    async def __get_metadata_components(cls, app: AppsModel) -> dict:
        return {
            "sender_details": Collection(
                name="sender_details",
                label="Sender Details",
                order=["email"],
                components=await cls.__get_sender_details_components(app)
            )
        }

    @classmethod
    async def __get_sender_details_components(cls, app:AppsModel) -> dict:
        return {
            "email": Collection(
                name="email",
                label="Email Sender Details",
                order=["name", "address", "reply_to"],
                components=await cls.__get_email_sender_components(app)
            )
        }

    @staticmethod
    async def __get_email_sender_components(app: AppsModel) -> dict:
        return {
            "name": SelectField(
                name="name",
                label="Email Sender Name",
                initialValue=app.email.sender.name,
                disabled=False
            ),
            "address": EmailInput(
                name="address",
                label="Email Sender Address",
                initialValue=app.email.sender.address,
                disabled=False
            ),
            "reply_to": EmailInput(
                name="reply_to",
                label="Reply To Address",
                initialValue=app.email.reply_to,
                disabled=False
            )
        }

    @staticmethod
    async def __get_callback_events_components(app: AppsModel):
        return {
            "email": SelectField(
                name="email",
                label="Email",
                initialValue=app.callback_events["email"] if "email" in app.callback_events and app.callback_events["email"] else None,
                mode=SelectMode.MULTIPLE,
                options=Option.from_enum(EmailEventStatus),
            ),
            "sms": SelectField(
                name="sms",
                label="SMS",
                initialValue=app.callback_events["sms"] if "sms" in app.callback_events and app.callback_events["sms"] else None,
                mode=SelectMode.MULTIPLE,
                options=Option.from_enum(SmsEventStatus),
            ),
            "push": SelectField(
                name="push",
                label="Push",
                initialValue=app.callback_events["push"] if "push" in app.callback_events and app.callback_events["push"] else None,
                mode=SelectMode.MULTIPLE,
                options=Option.from_enum(PushEventStatus),
            ),
            "whatsapp": SelectField(
                name="whatsapp",
                label="WhatsApp",
                initialValue=app.callback_events["whatsapp"] if "whatsapp" in app.callback_events and app.callback_events["whatsapp"] else None,
                mode=SelectMode.MULTIPLE,
                options=Option.from_enum(WhatsAppEventStatus),
            ),
        }

    @classmethod
    async def _get_components(cls, app: AppsModel):
        return {
            "id": SelectField(
                name="id",
                label="App ID",
                initialValue=app.id,
                disabled=True,
                rules=[Required]
            ),
            "name": SelectField(
                name="name",
                label="Name",
                initialValue=app.name,
                disabled=True,
                rules=[Required]
            ),
            "callback_url": SelectField(
                name="callback_url",
                label="Callback URL",
                initialValue=app.callback_url,
                disabled=False
            ),
            "callback_events": Collection(
                name="callback_events",
                label="Callback Events",
                order=["email", "sms", "push", "whatsapp"],
                components=await cls.__get_callback_events_components(app),
            ),
            "metadata": Collection(
                name="metadata",
                label="Meta Data",
                order=["sender_details"],
                components=await cls.__get_metadata_components(app)
            )
        }

    @classmethod
    async def get_instance(cls, app_id):
        app = await AppsRepository.get_app_by_id(app_id)
        components = await cls._get_components(app)
        return Collection(
            name="update_app",
            label="Update App",
            order=[
                "name",
                "callback_url",
                "callback_events",
                "metadata"
            ],
            components=components,
        )
