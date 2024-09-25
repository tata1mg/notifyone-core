from torpedo.exceptions import BadRequestException

from app.constants.callbacks import EmailEventStatus, SmsEventStatus, WhatsAppEventStatus, PushEventStatus
from app.repositories.apps import AppsRepository
from app.utilities.validators import validate_enum_values


class AppService:

    @classmethod
    async def list_app_names(cls):
        return await AppsRepository.filter_cols(columns=["name"], flat=True)

    @classmethod
    async def get_all_apps(cls):
        apps = await AppsRepository.filter_cols(columns=["id", "name", "callback_url", "metadata", "updated"])
        apps_data = list()
        for app in apps:
            apps_data.append(
                {
                    "id": app[0],
                    "app_name": app[1],
                    "callback_url": app[2],
                    "email_sender_address": app[3]["sender_details"]["email"]["address"],
                    "email_sender_name": app[3]["sender_details"]["email"]["name"],
                    "email_sender_reply_to": app[3]["sender_details"]["email"]["reply_to"],
                    "updated": app[4].strftime("%m/%d/%Y, %H:%M:%S")
                }
            )
        return {
            "title": "List of Tenants",
            "tenants": apps_data
        }

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

    @classmethod
    async def update_app(cls, request_payload):
        app_id = request_payload.get("id")
        if app_id is None:
            raise BadRequestException("App ID is mandatory param")

        # Get Webhook URL
        callback_url = request_payload.get("callback_url") or None

        # Get Callback Events
        callback_events = request_payload.get("callback_events") or dict()
        validate_enum_values(callback_events.get("email") or list(), EmailEventStatus, exec_class=BadRequestException)
        validate_enum_values(callback_events.get("sms") or list(), SmsEventStatus, exec_class=BadRequestException)
        validate_enum_values(callback_events.get("whatsapp") or list(), WhatsAppEventStatus,
                             exec_class=BadRequestException)
        validate_enum_values(callback_events.get("push") or list(), PushEventStatus, exec_class=BadRequestException)

        metadata = request_payload.get('metadata') or dict()
        sender_details = metadata.get('sender_details') or dict()

        # Get email sender details
        email_sender = sender_details.get('email') or dict()
        sender_name = email_sender.get('name')
        sender_address = email_sender.get('address')
        reply_to = email_sender.get('reply_to')

        if not (sender_name and sender_address and reply_to):
            raise BadRequestException(
                "Missing email configurations. `sender_name`, 'sender_address' and `reply_to` is mandatory")

        metadata_to_store = {
            "sender_details": {
                "email": {
                    "name": sender_name,
                    "address": sender_address,
                    "reply_to": reply_to
                }
            }
        }

        app = await AppsRepository.update_app(
            app_id, callback_url, callback_events, metadata_to_store
        )
        return {
            "id": app.id,
            "name": app.name,
            "message": "App updated successfully"
        }
