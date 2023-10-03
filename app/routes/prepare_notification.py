from sanic import Blueprint

from torpedo import Request, send_response

from app.services import PrepareNotification

notify_bp = Blueprint("Notify")


@notify_bp.route("/prepare-notification", methods=["POST"], name="prepare_notification")
async def prepare_notification(request: Request):
    results = await PrepareNotification.handle(request.json)
    return send_response(data=results)
