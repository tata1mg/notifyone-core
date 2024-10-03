from app.constants import NotificationChannels, Providers


class DashboardProvidersScreen:

    @classmethod
    async def get_configured_providers(cls):
        return {
            "title": "Page Heading",
            "sub_title": "Any other message",
            "providers": [
                {
                    "provider": "PLIVO",
                    "name": "Plivo SMS Provider",
                    "unique_identifier": "PLIVO_13123",
                    "channel": "Email",
                    "status": "active",
                    "last_updated": "Jan 11, 2024 @ 11:00 AM"
                },
                {
                    "provider": "SMS_COUNTRY",
                    "name": "Sms Country SMS Provider",
                    "unique_identifier": "PLIVO_13123",
                    "channel": "Email",
                    "status": "disabled",
                    "last_updated": "Jan 11, 2024 @ 11:00 AM"
                }
            ]
        }

    @classmethod
    async def get_channels_and_providers(cls):
        return {
            "message": "List for channels along with their respective providers",
            "channels": NotificationChannels.get_all_values(),
            "channel_providers": {
                NotificationChannels.EMAIL.value : {
                    "name": NotificationChannels.EMAIL.value.title(),
                    "code": NotificationChannels.EMAIL.value,
                    "providers": Providers.get_channel_providers(NotificationChannels.EMAIL)
                },
                NotificationChannels.SMS.value: {
                    "name": NotificationChannels.SMS.value.title(),
                    "code": NotificationChannels.SMS.value,
                    "providers": Providers.get_channel_providers(NotificationChannels.SMS)
                },
                NotificationChannels.PUSH.value: {
                    "name": NotificationChannels.PUSH.value.title(),
                    "code": NotificationChannels.PUSH.value,
                    "providers": Providers.get_channel_providers(NotificationChannels.PUSH)
                },
                NotificationChannels.WHATSAPP.value: {
                    "name": NotificationChannels.WHATSAPP.value.title(),
                    "code": NotificationChannels.WHATSAPP.value,
                    "providers": Providers.get_channel_providers(NotificationChannels.WHATSAPP)
                }
            }
        }