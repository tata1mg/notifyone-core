from app.constants import NotificationRequestLogStatus
from app.repositories.notification_request_log import NotificationRequestLogRepository


class NotificationRequestLogManager:

    @classmethod
    async def get_triggered_notifications(cls, notification_request_id: str):
        triggered_notifications = await NotificationRequestLogRepository.get_notification_request_log(
            notification_request_id=notification_request_id
        )
        data = list()
        for tn in triggered_notifications:
            if tn.status == NotificationRequestLogStatus.SUCCESS.value:
                tn.metadata = None
                tn.message = None
            tn_dict = await tn.to_dict()
            tn_dict['created'] = int(tn_dict['created'].timestamp())
            tn_dict['updated'] = int(tn_dict['updated'].timestamp())
            data.append(tn_dict)
        return data
