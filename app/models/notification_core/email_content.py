class EmailContentModel:

    def __init__(self, email_content_dict: dict):
        self.id = email_content_dict['id']
        self.name = email_content_dict['name']
        self.path = email_content_dict['path']
        self.description = email_content_dict['description']
        self.event_id = email_content_dict['event_id']
        self.subject = email_content_dict['subject']
        self.content = email_content_dict['content']
        self.updated_by = email_content_dict['updated_by']