from app.constants import NotificationChannels, EmailProviders, SmsProviders, PushProviders, WhatsappProviders

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
                    "status": "active/disabled",
                    "last_updated": "Jan 11, 2024 @ 11:00 AM"
                },
                {
                    "provider": "SMS_COUNTRY",
                    "name": "Sms Country SMS Provider",
                    "unique_identifier": "PLIVO_13123",
                    "channel": "Email",
                    "status": "active/disabled",
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
                    "providers": [provider.value for provider in EmailProviders]
                },
                NotificationChannels.SMS.value: {
                    "name": NotificationChannels.SMS.value.title(),
                    "code": NotificationChannels.SMS.value,
                    "providers": [provider.value for provider in SmsProviders]
                },
                NotificationChannels.PUSH.value: {
                    "name": NotificationChannels.PUSH.value.title(),
                    "code": NotificationChannels.PUSH.value,
                    "providers": [provider.value for provider in PushProviders]
                },
                NotificationChannels.WHATSAPP.value: {
                    "name": NotificationChannels.WHATSAPP.value.title(),
                    "code": NotificationChannels.WHATSAPP.value,
                    "providers": [provider.value for provider in WhatsappProviders]
                }
            }
        }