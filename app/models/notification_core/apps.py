class AppsModel:

    def __init__(self, apps_dict: dict):
        self.id = apps_dict['id']
        self.name = apps_dict['name']
        self.callback_url = apps_dict["callback_url"]
        self.callback_events = apps_dict["callback_events"]
        metadata = apps_dict['metadata'] or dict()
        email_sender_config = metadata.get("sender_details", dict()).get("email") or dict()
        self.email = EmailConfigurableDetails(email_sender_config)


class EmailConfigurableDetails:

    def __init__(self, configuration: dict):
        self.reply_to = configuration.get('reply_to') or None
        self.sender = EmailSender(configuration.get('name'), configuration.get('address'))


class EmailSender:

    def __init__(self, name, address):
        self.name = name
        self.address = address
