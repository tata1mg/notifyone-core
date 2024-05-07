from torpedo.constants import HTTPMethod

from sanic_openapi import openapi

from app.constants.callbacks import EmailEventStatus, SmsEventStatus, WhatsAppEventStatus, PushEventStatus
from app.routes.api_models.base_api_model import BaseApiModel


class CreateAppMetadataSenderDetailsEmailOpenApiModel:
    name = openapi.String(
        description="Sender name to be used in sending email", example="Tata 1mg",
        required=True
    )
    address = openapi.String(
        description="Sender email address to be used in sending email",
        example="sender@xyzmail.com", required=True
    )
    reply_to = openapi.String(
        description="Reply to email address for sending email", example="reply@xyzmail.com",
                              required=True
    )


class CreateAppMetadataSenderDetailsOpenApiModel:
    email = CreateAppMetadataSenderDetailsEmailOpenApiModel


class CreateAppMetadataOpenApiModel:
    sender_details = CreateAppMetadataSenderDetailsOpenApiModel


class CreateAppCallbackEventsEmailOpenApiModel:
    sent = openapi.String(description="Sent event", example=EmailEventStatus.SENT.value)
    delivered = openapi.String(description="Delivered event", example=EmailEventStatus.DELIVERED.value)


class CreateAppCallbackEventsSmsOpenApiModel:
    sent = openapi.String(description="Sent event", example=SmsEventStatus.SENT.value)
    delivered = openapi.String(description="Delivered event", example=SmsEventStatus.DELIVERED.value)


class CreateAppCallbackEventsPushOpenApiModel:
    pass


class CreateAppCallbackEventsWhatsappOpenApiModel:
    sent = openapi.String(description="Sent event", example=WhatsAppEventStatus.SENT.value)
    delivered = openapi.String(description="Delivered event", example=WhatsAppEventStatus.DELIVERED.value)


class CreateAppCallbackEventsOpenApiModel:
    email = openapi.Array(
        description="List of events to subscribe for emails",
        items=EmailEventStatus.DELIVERED.value
    )
    sms = openapi.Array(
        description="List of events to subscribe for sms notifications",
        items=SmsEventStatus.DELIVERED.value
    )
    push = openapi.Array(
        description="List of events to subscribe for push notifications",
        items=""
    )
    whatsapp = openapi.Array(
        description="List of events to subscribe for whatsapp notifications",
        items=WhatsAppEventStatus.DELIVERED.value
    )


class CreateAppApiModel(BaseApiModel):

    _uri = "/apps"
    _name = "create_app"
    _method: str = HTTPMethod.POST.value
    _summary = "API to create a new app"
    _description = "The API can be used to create new apps in the system"

    class RequestBodyOpenApiModel:
        name = openapi.String(description="App name provided in the request body", example="test_app")
        callback_url = openapi.String(description="Webhook URL to receive status updates", example="https://example.com/webhook")
        callback_events = CreateAppCallbackEventsOpenApiModel
        metadata = CreateAppMetadataOpenApiModel

    class ResponseBodyOpenApiModel:
        id = openapi.Integer(description="ID of the newly created app", example=111)
        name = openapi.String(description="App name provided in the request body", example="test_app")
        message = openapi.String(description="Message string", example="App created successfully")
