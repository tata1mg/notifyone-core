from torpedo import Request,send_response
from sanic import Blueprint
from app.manager.push_notification_manager import PushManager
from app.exceptions import RequiredParamsException

push_apis = Blueprint("PushAPIs")


@push_apis.route("/push/template", methods=["PUT"], name="update_push_template")
async def update_push_template(request: Request):
    payload = request.custom_json()
    user_email = request.ctx.user
    push_template_id = payload.get("id")
    if not push_template_id:
        raise RequiredParamsException("template id is missing in payload")
    data = payload.get("data")
    if not data:
        raise RequiredParamsException("data is missing in payload")
    await PushManager.update_push_notification(
        push_template_id, data, user_email, payload=payload
    )
    message = {"message": "push notification has been updated sucessfully"}
    return send_response(message)

@push_apis.route(
    "/push/template/preview", methods=["POST"], name="preview_push_template"
)
async def get_push_template_previews(request: Request):
    payload = request.custom_json()
    event_id = payload.get("event_id")
    if not event_id:
        raise RequiredParamsException("event_id id is missing in payload")
    body, title, data = payload.get("body"), payload.get("title"), payload.get("data")
    result = await PushManager.get_push_template_previews(event_id, body, title, data)
    return send_response(result)
