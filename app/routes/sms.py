from torpedo import Request, send_response
from sanic import Blueprint
from app.manager.sms_manager import SmsManager
from app.exceptions import RequiredParamsException

sms_apis = Blueprint("SmsAPIs")


@sms_apis.route("/sms/template", methods=["PUT"], name="update_sms_template")
async def update_sms_template(request: Request):
    payload = request.custom_json()
    user_email = "temp@ns.com"
    sms_template_id = payload.get("id")
    if not sms_template_id:
        raise RequiredParamsException("template id is missing in payload")
    data = payload.get("data")
    if not data:
        raise RequiredParamsException("data is missing in payload")
    await SmsManager.update_sms_template(
        sms_template_id, data, user_email, payload=payload
    )
    message = {"message": "sms template has been updated sucessfully"}
    return send_response(message)

@sms_apis.route(
    "/sms/template/preview", methods=["POST"], name="preview_sms_template"
)
async def get_sms_template_previews(request: Request):
    payload = request.custom_json()
    user_email = "temp@ns.com"
    content, event_name, data = (
        payload.get("content"),
        payload.get("event_name"),
        payload.get("data"),
    )
    result = await SmsManager.get_sms_template_previews(
        content, event_name, user_email, data
    )
    return send_response(result)    
