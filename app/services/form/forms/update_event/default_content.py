from app.models.notification_core import EmailContentModel
from app.models.notification_core import SmsContentModel
from app.models.notification_core import PushNotificationModel
from app.models.notification_core import WhatsappContentModel

NoneEmailContentModel = EmailContentModel({
    "id": None,
    "name": None,
    "path": None,
    "description": None,
    "event_id": None,
    "subject": None,
    "content": None,
    "updated_by": None
})

NoneSmsContentModel = SmsContentModel({
    "id": None,
    "event_id": None,
    "content": None,
    "updated_by": None
})

NonePushContentModel = PushNotificationModel({
    "id": None,
    "event_id": None,
    "title": None,
    "body": None,
    "target": None,
    "image": None,
    "type": None,
    "device_type": None,
    "device_version": None,
    "updated_by": None,
    "created": None,
    "updated": None
})

NoneWhatsappContentModel = WhatsappContentModel({
    "id": None,
    "event_id": None,
    "name": None,
    "updated_by": None,
    "variable_mapping": None
})


