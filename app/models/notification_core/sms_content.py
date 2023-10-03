class SmsContentModel:

    def __init__(self, sms_content_dict: dict):
        self.id = sms_content_dict['id']
        self.event_id = sms_content_dict['event_id']
        self.content = sms_content_dict['content']
        self.updated_by = sms_content_dict['updated_by']