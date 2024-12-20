from torpedo.exceptions import BadRequestException

from app.constants import NotificationChannels, Providers

from app.repositories.providers import ProvidersRepository
from app.utilities.utils import epoch_to_str_date


class DashboardProvidersScreen:

    @classmethod
    def _verify_input_configuration(cls, configuration: dict, sample: dict):
        for key in sample.keys():
            if key in configuration and isinstance(sample[key], type(configuration[key])):
                pass
            else:
                raise BadRequestException("Config details missing")
            if isinstance(sample[key], dict):
                cls._verify_input_configuration(configuration[key], sample[key])

    @classmethod
    async def add_new_provider(cls, data):
        # Input validation
        unique_identifier = data.get("unique_identifier")
        channel = data.get("channel") or None
        provider = data.get("provider") or None
        channel_enum = NotificationChannels.get_enum(channel)
        provider_enum = Providers.get_enum_from_code(provider)
        configuration = data.get("configuration") or dict()
        if not unique_identifier:
            raise BadRequestException("unique_identifier missing")
        if not channel_enum:
            raise BadRequestException("Invalid channel")
        if not provider_enum:
            raise BadRequestException("Invalid provider")
        if not configuration:
            raise BadRequestException("Missing configuration")

        # Validate providers configuration
        provider_config_sample = provider_enum.value["configuration"]
        cls._verify_input_configuration(configuration, provider_config_sample)

        # Save details
        provider_model = await ProvidersRepository.add_new_provider(channel_enum, provider_enum, unique_identifier, configuration)

        return {
            "message": "Provider saved successfully",
            "provider": {
                "provider": provider_model.provider,
                "unique_identifier": provider_model.unique_identifier,
                "channel": provider_model.channel,
                "status": provider_model.status.value,
                "last_updated": epoch_to_str_date(provider_model.updated)
            }
        }

    @classmethod
    async def update_provider(cls, data):
        # Input validation
        unique_identifier = data.get("unique_identifier")
        configuration = data.get("configuration") or dict()
        disable = True if data.get("enabled") is False else False
        if not unique_identifier:
            raise BadRequestException("unique_identifier missing")
        if not configuration:
            raise BadRequestException("Missing configuration")

        # Fetch existing row
        provider_model = await ProvidersRepository.get_provider_by_unique_id(unique_identifier)

        channel = provider_model.channel
        provider_enum = Providers.get_enum_from_code(provider_model.provider)

        # Validate providers configuration
        provider_config_sample = provider_enum.value["configuration"]
        cls._verify_input_configuration(configuration, provider_config_sample)

        # Update details
        updated_provider = await ProvidersRepository.update_provider(unique_identifier, disable=disable, configuration=configuration)

        return {
            "message": "Provider updated successfully",
            "provider": {
                "provider": updated_provider.provider,
                "unique_identifier": updated_provider.unique_identifier,
                "channel": updated_provider.channel,
                "status": updated_provider.status.value,
                "last_updated": epoch_to_str_date(updated_provider.updated)
            }
        }

    @classmethod
    async def get_configured_providers(cls, limit, offset):
        final_list = list()
        providers = await ProvidersRepository.get_configured_providers(limit=limit, offset=offset)
        for provider in providers:
            final_list.append(
                {
                    "name": Providers.get_enum_from_code(provider.provider).value["name"],
                    "provider": provider.provider,
                    "unique_identifier": provider.unique_identifier,
                    "channel": provider.channel,
                    "status": provider.status.value,
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
        channel_providers = dict()
        for channel in NotificationChannels.get_all_values():
            channel_providers[channel] = {
                "name": channel.title(),
                "code": channel,
                "providers": Providers.get_channel_providers_details(NotificationChannels.get_enum(channel))
            }
        return {
            "message": "List for channels along with their respective providers",
            "channels": NotificationChannels.get_all_values(),
            "channel_providers": channel_providers
        }
