class WhatsappContentModel:

    def __init__(self, whatsapp_content_dict: dict):
        self.id = whatsapp_content_dict['id']
        self.event_id = whatsapp_content_dict['event_id']
        self.name = whatsapp_content_dict['name']
        self.updated_by = whatsapp_content_dict['updated_by']