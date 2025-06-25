from torpedo import Request, send_response
from sanic import Blueprint
from app.manager.email_manager import EmailManager
from app.exceptions import RequiredParamsException
from app.routes.middleware.authentication import HttpRequestAuthentication

email_blueprint = Blueprint("email", version=4)
email_api_with_auth = Blueprint("EmailAPIs")

@email_api_with_auth.on_request
async def request_authenticator(request: Request):
    """
    Middleware to authenticate each incoming request of create event
    """
    await HttpRequestAuthentication.examine_request(request)


@email_api_with_auth.route("/email/template", methods=["PUT"], name="update_email_template")
async def update_email_template(request: Request):
    payload = request.custom_json()
    user_email = "admin@ns.com"
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

@email_api_with_auth.route(
    "/email/template/preview", methods=["POST"], name="preview email_template"
)
async def get_email_template_previews(request: Request):
    payload = request.custom_json()
    user_email = "admin@ns.com"
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

@email_api_with_auth.route(
    "/email/include/template", methods=["POST"], name="create_include_email_template"
)
async def create_include_email_template(request: Request):
    payload = request.custom_json()
    user_email = "admin@ns.com"
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

@email_blueprint.route("/email/template", methods=["GET"], name="get_email_template")
async def get_email_template(request: Request):
    request_params = request.request_params()
    template_id = request_params.get("id")
    data = await EmailManager.get_email_template_by_id(template_id)
    return send_response(data=data)
    
@email_api_with_auth.route("/email/subtemplate/<id:int>", methods=["PUT"], name="update_email_subtemplate")
async def update_email_subtemplate(request: Request, id: int):
    payload = request.custom_json()
    user_email = request.ctx.user
    content, description = (
        payload.get("content"),
        payload.get("description"),
    )
    result = await EmailManager.update_email_subtemplate(int(id), content, description, user_email)
    return send_response(result)
    
@email_api_with_auth.route("/email/preview", methods=["POST"], name="preview_email_subtemplate")
async def preview_email_subtemplate(request: Request):
    request_params = request.request_params()
    payload = request.custom_json()
    start = request_params.get("start")
    size = request_params.get("size")
    template_id = payload.get("id")
    description = payload.get("description")
    content = payload.get("content")
    user_email = request.ctx.user
    result = await EmailManager.preview_email_subtemplate(template_id, description, content, user_email, int(start), int(size))
    return send_response(result)

