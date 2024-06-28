from sanic import Blueprint
from sanic_openapi import openapi
from torpedo import Request, send_response
from torpedo.exceptions import BadRequestException
from app.services import Events
from app.services.email import EmailHandler
from app.utilities import current_epoch
from app.routes.api_models.event import CreateEventApiModel

event_blueprint = Blueprint("Events")


@event_blueprint.route("/events/custom", methods=["GET"], name="get_events_custom")
async def get_events_custom(request: Request):
    request_params = request.request_params()
    attributes = request_params.get("attributes") or ""
    attributes = attributes.split(",")
    attributes = [str(attr).strip() for attr in attributes]
    data = await Events.get_events_custom(attributes)
    return send_response(data=data)

@event_blueprint.route(
    "/events/handle-email-template-update",
    methods=["POST"],
    name="handle_email_template_update",
)
async def handle_email_template_update(request: Request):
    request_payload = request.custom_json()
    template_version = request_payload.get("template_version") or current_epoch()
    await EmailHandler.handle_email_template_update(template_version)
    data = {"message": "success"}
    return send_response(data=data)

@event_blueprint.route(CreateEventApiModel.uri(), methods=[CreateEventApiModel.http_method()], name=CreateEventApiModel.name())
@openapi.definition(
    summary=CreateEventApiModel.summary(),
    description=CreateEventApiModel.description(),
    body={
        CreateEventApiModel.request_content_type(): CreateEventApiModel.RequestBodyOpenApiModel
    },
    response={
        CreateEventApiModel.response_content_type(): CreateEventApiModel.ResponseBodyOpenApiModel
    }
)
async def create_event(request: Request):
    data = request.custom_json()
    data["user_email"] = "temp@ns.com"
    result = await Events.create_event(data)
    return send_response(result)

@event_blueprint.route("/event/add_action", methods=["PUT"], name="update_event")
async def update_event(request: Request):
    data = request.custom_json()
    data["user_email"] = "temp@ns.com"
    result = await Events.add_new_action_to_event(data)
    return send_response(result)

@event_blueprint.route("/event/<id:int>", methods=["GET"], name="get_event_by_id")
async def get_event_by_id(request: Request, id: int):
    channel_name = request.args.get("channel")
    event_id = int(id)
    if not event_id:
        raise BadRequestException("event id cannot be empty")
    result = await Events.get_event(event_id=event_id, channel_name=channel_name)
    return send_response(result)

@event_blueprint.route("/events", methods=["GET"], name="get_event")
async def get_events(request: Request):
    result = await Events.get_events(request.args)
    return send_response(result)

@event_blueprint.route(
    "/event/<event_id:int>", methods=["DELETE"], name="delete_event_with_id"
)
async def delete_event(request: Request, event_id: int):
    user_email = "temp@ns.com"
    result = await Events.delete_event(event_id, user_email)
    return send_response(result)
