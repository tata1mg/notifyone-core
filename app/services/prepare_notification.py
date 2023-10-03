from typing import Any, Dict

from app.services.notification_request import NotificationRequest


class PrepareNotification:
    @classmethod
    async def handle(cls, data: Dict[str, Any]) -> bool:
        return await NotificationRequest.handle_notification_request_sync(data)
