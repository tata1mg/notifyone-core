from app.constants import NotificationChannels, Providers

from app.repositories.providers import ProvidersRepository
from app.utilities.utils import epoch_to_str_date


class DashboardProvidersScreen:

    @classmethod
    async def get_configured_providers(cls, limit, offset):
        final_list = list()
        providers = await ProvidersRepository.get_configured_providers(limit=limit, offset=offset)
        for provider in providers:
            final_list.append(
                {
                    "provider": provider.provider,
                    "unique_identifier": provider.unique_identifier,
                    "channel": provider.channel,
                    "status": provider.status,
                    "last_updated": epoch_to_str_date(provider.updated)
                }
            )
        total_count = await ProvidersRepository.total_count()
        return {
            "title": "Configured Providers",
            "sub_title": "List of all active/disabled providers configured in the system",
            "limit": limit,
            "offset": offset,
            "total": total_count,
            "providers": final_list
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