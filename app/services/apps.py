from torpedo.exceptions import BadRequestException

from app.constants.callbacks import EmailEventStatus, SmsEventStatus, WhatsAppEventStatus, PushEventStatus
from app.repositories.apps import AppsRepository
from app.utilities.validators import validate_enum_values


class AppService:

    @classmethod
    async def list_app_names(cls):
        return await AppsRepository.filter_cols(columns=["name"], flat=True)

    @classmethod
    async def create_app(cls, request_payload):
        # The info must contain email sender details (name, address and reply_to)
        app_name = request_payload.get("name")
        if not app_name:
            raise BadRequestException("App name is mandatory param")

        # Get Webhook URL
        callback_url = request_payload.get("callback_url") or None

        # Get Callback Events
        callback_events = request_payload.get("callback_events") or dict()
        validate_enum_values(callback_events.get("email") or list(), EmailEventStatus, exec_class=BadRequestException)
        validate_enum_values(callback_events.get("sms") or list(), SmsEventStatus, exec_class=BadRequestException)
        validate_enum_values(callback_events.get("whatsapp") or list(), WhatsAppEventStatus, exec_class=BadRequestException)
        validate_enum_values(callback_events.get("push") or list(), PushEventStatus, exec_class=BadRequestException)

        metadata = request_payload.get('metadata') or dict()
        sender_details = metadata.get('sender_details') or dict()

        # Get email sender details
        email_sender = sender_details.get('email') or dict()
        sender_name = email_sender.get('name')
        sender_address = email_sender.get('address')
        reply_to = email_sender.get('reply_to')

        if not (sender_name and sender_address and reply_to):
            raise BadRequestException("Missing email configurations. `sender_name`, 'sender_address' and `reply_to` is mandatory")

        metadata_to_store = {
            "sender_details": {
                "email": {
                    "name": sender_name,
                    "address": sender_address,
                    "reply_to": reply_to
                }
            }
        }

        app = await AppsRepository.create_app(
            app_name, callback_url, callback_events, metadata_to_store
        )
        return {
            "id": app.id,
            "name": app_name,
            "message": "App created successfully"
        }
