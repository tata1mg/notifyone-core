from torpedo.exceptions import BadRequestException, NotFoundException

from app.constants import NotificationChannels, Providers
from app.repositories.providers_default_priority import ProvidersDefaultPriorityRepository
from app.repositories.providers import ProvidersRepository
from app.repositories.providers_dynamic_priority import ProvidersDynamicPriorityRepository
from app.utilities.utils import is_valid_python_expression


class DashboardSettingsScreen:

    @classmethod
    async def upsert_default_provider_priority_for_channel(cls, data: dict):
        channel = data.get("channel") or None
        channel_enum = NotificationChannels.get_enum(channel)
        providers_priority = data.get("providers_priority") or list()
        disable = data.get("disable") or False
        if not channel_enum:
            raise BadRequestException("Invalid channel value")
        if not providers_priority:
            raise BadRequestException("Providers priority can't be empty. If you don't want to have a priority, disable the priorty rule instead")
        providers_for_channel = await ProvidersRepository.get_providers_for_channel(channel_enum, include_disabled=False)
        providers_dict = dict()
        for provider in providers_for_channel:
            providers_dict[provider.unique_identifier] = provider
        for provider_unique_identifier in providers_priority:
            if provider_unique_identifier not in providers_dict:
                raise BadRequestException("Unique identifier {} is not configured OR not active. Please check".format(provider_unique_identifier))

        try:
            existing_priority = await ProvidersDefaultPriorityRepository.get_channel_priority(channel_enum)
        except NotFoundException:
            existing_priority = None

        if not existing_priority:
            await ProvidersDefaultPriorityRepository.add_new_priority(channel_enum, providers_priority)
        else:
            await ProvidersDefaultPriorityRepository.update_priority(channel_enum, disable=disable, priority=providers_priority)
        return {
            "message": "Priority created/updated successfully"
        }

    @classmethod
    async def get_default_priority_all(cls):
        response_data = {
            "title": "Channel Providers Priority",
            "channels": []
        }
        for channel in NotificationChannels.get_all_values():
            priority_data = None
            channel_providers_map = dict()
            try:
                priority_data = await ProvidersDefaultPriorityRepository.get_channel_priority(NotificationChannels.get_enum(channel))
            except NotFoundException:
                pass
            if priority_data:
                channel_providers = await ProvidersRepository.get_providers_for_channel(
                    NotificationChannels.get_enum(channel), include_disabled=True
                )
                for provider in channel_providers:
                    channel_providers_map[provider.unique_identifier] = {
                        "name": Providers.get_enum_from_code(provider.provider).value["name"],
                        "code": provider.provider,
                        "logo": Providers.get_enum_from_code(provider.provider).value["logo"]
                    }
            response_data["channels"].append(
                {
                    "name": str(channel).title(),
                    "code": channel,
                    "providers_priority": [channel_providers_map[provider_identifier] for provider_identifier in priority_data.priority] if priority_data else []
                }
            )
        return response_data

    @classmethod
    async def upsert_dynamic_provider_priority_for_channel(cls, data: dict):
        channel = data.get("channel") or None
        channel_enum = NotificationChannels.get_enum(channel)
        dynamic_priority = data.get("dynamic_priority") or ""
        disable = data.get("disable") or False
        if not channel_enum:
            raise BadRequestException("Invalid channel value")
        if not dynamic_priority:
            raise BadRequestException(
                "Providers dynamic priority can't be empty. If you don't want to have a priority, disable the priority rule instead"
            )

        # Validate to check if dynamic_priority is a valid python one-liner statement
        if not is_valid_python_expression(dynamic_priority):
            raise BadRequestException("Input dynamic priority is not a valid python expression. Please input a valid python expression")

        try:
            existing_priority = await ProvidersDynamicPriorityRepository.get_channel_priority(channel_enum)
        except NotFoundException:
            existing_priority = None

        if not existing_priority:
            await ProvidersDynamicPriorityRepository.add_new_priority(channel_enum, dynamic_priority)
        else:
            await ProvidersDynamicPriorityRepository.update_priority(channel_enum, disable=disable, priority_logic=dynamic_priority)

        return {
            "message": "Priority created/updated successfully"
        }

    @classmethod
    async def get_dynamic_priority_all(cls):
        response_data = {
            "title": "Channel Providers Priority",
            "channels": []
        }
        for channel in NotificationChannels.get_all_values():
            try:
                priority_data = await ProvidersDynamicPriorityRepository.get_channel_priority(
                    NotificationChannels.get_enum(channel)
                )
            except NotFoundException:
                priority_data = None
            response_data["channels"].append(
                {
                    "name": str(channel).title(),
                    "code": channel,
                    "dynamic_priority": priority_data.priority_logic if priority_data else ""
                }
            )
        return response_data
