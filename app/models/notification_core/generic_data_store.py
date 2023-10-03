class GenericDataStoreModel:

    def __init__(self, generic_data_store_dict: dict):
        self.id = generic_data_store_dict['id']
        self.event_id=generic_data_store_dict['event_id']
        self.category = generic_data_store_dict['category']
        self.identifier = generic_data_store_dict['identifier']
        self.data = generic_data_store_dict['data']
        self.updated_by = generic_data_store_dict['updated_by']
        self.created = generic_data_store_dict['created']
        self.updated = generic_data_store_dict['updated']