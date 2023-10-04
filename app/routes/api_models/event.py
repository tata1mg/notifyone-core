from app.routes.api_models.base_api_model import BaseApiModel
from torpedo.constants import HTTPMethod

from sanic_openapi import openapi


class CreateEventEmailOpenApiModel:
    description = openapi.String(description="Description of your event", example="This is test event", required=True)
    subject = openapi.String(description="Email subject", example="Regarding your Order {{order.order_id}}", required=True)
    content = openapi.String(description="Email body", example="Your order {{order.order_id}} has been processed", required=True)


class CreateEventSmsOpenApiModel:
    content = openapi.String(description="Email body", example="Your order {{order.order_id}} has been processed",
                             required=True)


class CreateEventPushOpenApiModel:
    title = openapi.String(description="Push message title", example="Order update", required=True)
    body = openapi.String(description="Push message body text", example="Order {{order.order_id}} has been delivered", required=True)


class CreateEventWhatsappOpenApiModel:
    name = openapi.String(description="Whatsapp template name for Interkt", example="order_delivered", required=True)


class CreateEventActionOpenApiModel:
    email = openapi.Integer(descritpion="1 denotes that email channel is active, 0 denotes it's disabled", example=1)
    sms = openapi.Integer(descritpion="1 denotes that sms channel is active, 0 denotes it's disabled", example=1)
    push = openapi.Integer(descritpion="1 denotes that push channel is active, 0 denotes it's disabled", example=1)
    whatsapp = openapi.Integer(descritpion="1 denotes that whatsapp channel is active, 0 denotes it's disabled", example=1)


class CreateEventTriggerLimitOpenApiModel:
    email = openapi.Integer(descritpion="-1 denotes that there is no limit on how many times this event can be triggered for a `source_identifier, any other integer limits it to that number`", example=1)
    sms = openapi.Integer(descritpion="-1 denotes that there is no limit on how many times this event can be triggered for a `source_identifier, any other integer limits it to that number`", example=1)
    push = openapi.Integer(descritpion="-1 denotes that there is no limit on how many times this event can be triggered for a `source_identifier, any other integer limits it to that number`", example=1)
    whatsapp = openapi.Integer(
        descritpion="-1 denotes that there is no limit on how many times this event can be triggered for a `source_identifier, any other integer limits it to that number`",
        example=1)


class CreateEventApiModel(BaseApiModel):

    _uri = "/event/create"
    _name = "create_event"
    _method: str = HTTPMethod.POST.value
    _summary = "API to create a new event"
    _description = "The API can be used to create new events in the system"

    class RequestBodyOpenApiModel:
        event_name = openapi.String(description="Event name", example="test_event", required=True)
        app_name = openapi.String(description="App name", example="test_app", required=True)
        email = CreateEventEmailOpenApiModel
        sms = CreateEventSmsOpenApiModel
        push = CreateEventPushOpenApiModel
        whatsapp = CreateEventWhatsappOpenApiModel
        priority = openapi.String(description="Priority for this event. Priority can be one of these values - critical/high/medium/low", example="high", required=True)
        event_type = openapi.String(description="Type for this event. Type can be one of these values - promotional/transactional/other", example="transactional", required=True)
        user_email = openapi.String(description="Email ID of the user requesting to create the event", example="test@test.com", required=True)

    class ResponseBodyOpenApiModel:
        event_id = openapi.String(description="Event ID generated for this event", example=111, required=True)
        event_name = openapi.String(description="Event name", example="test_event", required=True)
        app_name = openapi.String(description="App name", example="test_app", required=True)
        action = CreateEventActionOpenApiModel
        trigger_limit = CreateEventWhatsappOpenApiModel
        created_by = openapi.String(description="Email ID of the user requesting to create the event", example="test@test.com")
