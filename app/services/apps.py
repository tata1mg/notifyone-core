from torpedo.exceptions import BadRequestException

from app.repositories.apps import AppsRepository


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

        info = request_payload.get('info') or dict()
        email_info = info.get('email') or dict()
        sender_name = email_info.get('sender_name')
        sender_address = email_info.get('sender_address')
        reply_to = email_info.get('reply_to')
        if not (sender_name and sender_address and reply_to):
            raise BadRequestException("Missing email configurations. `sender_name`, 'sender_address' and `reply_to` is mandatory")

        info_to_store = {
            "email": {
                "sender_name": sender_name,
                "sender_address": sender_address,
                "reply_to": reply_to
            }
        }

        app = await AppsRepository.create_app(app_name, info_to_store)
        return {
            "id": app.id,
            "name": app_name,
            "message": "App created successfully"
        }
