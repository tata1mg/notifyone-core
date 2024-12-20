from typing import List

from torpedo.exceptions import NotFoundException

from app.constants import NotificationChannels
from app.repositories.providers import ProvidersRepository
from app.repositories.providers_default_priority import ProvidersDefaultPriorityRepository
from app.repositories.providers_dynamic_priority import ProvidersDynamicPriorityRepository


class ChannelPartners:

    @classmethod
    async def get_channel_partners_config_for_channels(cls, channels: List[NotificationChannels]):
        response = dict()
        for available_channel in NotificationChannels.get_all_values():
            response[available_channel] = {
                "gateways": [],
                "default_priority": [],
                "dynamic_priority": ""
            }
        for channel in channels:
            providers = await ProvidersRepository.get_providers_for_channel(channel)
            try:
                default_priority = await ProvidersDefaultPriorityRepository.get_channel_priority(channel)
            except NotFoundException:
                default_priority = []
            try:
                dynamic_priority = await ProvidersDynamicPriorityRepository.get_channel_priority(channel)
            except NotFoundException:
                dynamic_priority = ""
            for provider in providers:
                details = {
                    "id": provider.id,
                    "unique_identifier": provider.unique_identifier,
                    "gateway": provider.provider,
                    "configuration": provider.configuration
                }
                response[channel.value]["gateways"].append(details)
            if default_priority:
                response[channel.value]["default_priority"] = default_priority.priority
            if dynamic_priority:
                response[channel.value]["dynamic_priority"] = dynamic_priority.priority_logic
        return response
