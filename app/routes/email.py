from torpedo import Request, send_response
from sanic import Blueprint
from app.manager.email_manager import EmailManager
from app.exceptions import RequiredParamsException

email_apis = Blueprint("EmailAPIs")


@email_apis.route("/email/template", methods=["PUT"], name="update_email_template")
async def update_email_template(request: Request):
    payload = request.custom_json()
    user_email = request.ctx.user
    email_template_id = payload.get("id")
    if not email_template_id:
        raise RequiredParamsException("template id is missing in payload")
    data = payload.get("data")
    if not data:
        raise RequiredParamsException("data is missing in payload")
    result = await EmailManager.update_email_template(
        email_template_id, user_email, data, payload=payload
    )
    return send_response(result)

@email_apis.route(
    "/email/template/preview", methods=["POST"], name="preview email_template"
)
async def get_email_template_previews(request: Request):
    payload = request.custom_json()
    user_email = request.ctx.user
    template_id = payload.get("id")
    if not template_id:
        raise RequiredParamsException("template id is missing in payload")
    subject, content, data = (
        payload.get("subject"),
        payload.get("content"),
        payload.get("data"),
    )
    result = await EmailManager.get_email_template_previews(
        subject, content, template_id, user_email, data
    )
    return send_response(result)

@email_apis.route(
    "/email/include/template", methods=["POST"], name="create_include_email_template"
)
async def create_include_email_template(request: Request):
    payload = request.custom_json()
    user_email = request.ctx.user
    name, content, description, subject = (
        payload.get("name"),
        payload.get("content"),
        payload.get("description"),
        payload.get("subject"),
    )
    result = await EmailManager.include_email_template(
        name, content, description, subject, user_email
    )
    return send_response(result)
