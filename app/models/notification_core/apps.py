class AppsModel:

    def __init__(self, apps_dict: dict):
        self.id = apps_dict['id']
        self.name = apps_dict['name']
        info = apps_dict['info']
        email_config = info.get('email') or dict()
        self.email = EmailConfigurableDetails(email_config)


class EmailConfigurableDetails:

    def __init__(self, configuration: dict):
        self.reply_to = configuration.get('reply_to') or None
        self.sender = EmailSender(configuration.get('sender_name'), configuration.get('sender_address'))


class EmailSender:

    def __init__(self, name, address):
        self.name = name
        self.address = address
