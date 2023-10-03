class PushNotificationModel:

    def __init__(self, push_notification_dict: dict):
        self.id = push_notification_dict['id']
        self.event_id = push_notification_dict['event_id']
        self.title = push_notification_dict['title']
        self.body = push_notification_dict['body']
        self.target = push_notification_dict['target']
        self.image = push_notification_dict['image']
        self.device_type = push_notification_dict['device_type']
        self.device_version = push_notification_dict['device_version']
        self.updated_by = push_notification_dict['updated_by']
        self.created = push_notification_dict['created']
        self.updated = push_notification_dict['updated']
