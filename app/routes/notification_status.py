from sanic import Blueprint
from torpedo import Request, send_response
from torpedo.exceptions import BadRequestException

from app.constants import ErrorMessages
from app.manager.notification_request_log import NotificationRequestLogManager


notification_status_blueprint = Blueprint("NotificationStatus")


@notification_status_blueprint.route("/notifications/<notification_request_id:str>", methods=["GET"], name='get_notification_status')
async def get_notification_status(request: Request, notification_request_id: str):
    if not notification_request_id:
        raise BadRequestException(ErrorMessages.MISSING_REQUIRED_PARAM.value)
    notifications = await NotificationRequestLogManager.get_triggered_notifications(notification_request_id)
    data = {
        "notifications": notifications
    }
    return send_response(data=data)
