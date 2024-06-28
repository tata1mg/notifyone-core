from torpedo import Request, send_response
from sanic import Blueprint
from app.manager.whatsapp_manager import WhatsappManager
from app.exceptions import RequiredParamsException

whatsapp_apis = Blueprint("WhatsappAPIs")


@whatsapp_apis.route(
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
