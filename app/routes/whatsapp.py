from torpedo import Request, send_response
from sanic import Blueprint
from app.manager.whatsapp_manager import WhatsappManager
from app.exceptions import RequiredParamsException
from app.routes.middleware.authentication import HttpRequestAuthentication

whatsapp_apis_with_auth = Blueprint("WhatsappAPIs")

@whatsapp_apis_with_auth.on_request
async def request_authenticator(request: Request):
    """
    Middleware to authenticate each incoming request of create event
    """
    await HttpRequestAuthentication.examine_request(request)


@whatsapp_apis_with_auth.route(
    "/whatsapp/template", methods=["PUT"], name="update_whatsapp_template"
)
async def update_whatsapp_template(request: Request):
    payload = request.custom_json()
    user_email = "temp@ns.com"
    whatsapp_template_id = payload.get("id")
    if not whatsapp_template_id:
        raise RequiredParamsException("template id is missing in payload")
    await WhatsappManager.update_whatsapp_table(
        whatsapp_template_id, user_email, payload=payload
    )
    message = {"message": "whatsapp table has been updated sucessfully"}
    return send_response(message) 
