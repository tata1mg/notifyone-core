class ProviderModel:

    def __init__(self, provider_dict: dict):
        self.id = provider_dict['id']
        self.unique_identifier = provider_dict['unique_identifier']
        self.provider = provider_dict['provider']
        self.channel = provider_dict['channel']
        self.status = provider_dict['status']
        self.configuration = provider_dict['configuration']
        self.created = provider_dict['created']
        self.updated = provider_dict['updated']
