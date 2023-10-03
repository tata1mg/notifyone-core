from app.constants import EventPriority

class EventModel:

    def __init__(self, event_dict: dict):
        self.id = event_dict['id']
        self.app_name = event_dict['app_name']
        self.event_name = event_dict['event_name']
        self.actions = event_dict['actions']
        self.subject = event_dict['subject']
        self.triggers_limit = event_dict['triggers_limit']
        self.event_type = event_dict['event_type']
        self.meta_info = event_dict['meta_info']
        self.is_deleted = event_dict.get('is_deleted', False)
        self.updated_by = event_dict['updated_by']
        self.created = event_dict['created']
        self.updated = event_dict['updated']
        self.priority = EventPriority(self.meta_info.get('priority'))

    def custom_dict(self, attributes):
        data = {
            'id': self.id,
            'app_name': self.app_name,
            'event_name': self.event_name
        }
        for attr in attributes:
            data[attr] = getattr(self, attr)
        return data

    def get_active_channels(self):
        return [key for key in self.actions if self.actions[key] == 1]

    def mute_channels(self, channels: list):
        for channel in channels:
            if channel in self.actions:
                self.actions[channel] = 0

    def is_trigger_limit_enabled(self) -> bool:
        for limit in self.triggers_limit.values():
            if limit != -1:
                return True
        return False

    def is_trigger_limit_enabled_for_any_active_channel(self) -> bool:
        active_channels = self.get_active_channels()
        for channel in active_channels:
            if channel in self.triggers_limit and self.triggers_limit[channel] != -1:
                return True
        return False

    def is_trigger_limit_enabled_for_channel(self, channel) -> bool:
        if channel in self.triggers_limit and self.triggers_limit[channel] != -1:
            return True
        return False

    @classmethod
    def attributes_available_to_fetch(cls):
        return ['id', 'app_name', 'event_name', 'actions', 'meta_info', 'event_type']