import copy

from tortoise.exceptions import IntegrityError
from torpedo.exceptions import NotFoundException, BadRequestException
from tortoise_wrapper.wrappers import ORMWrapper

from app.constants import NotificationChannels, Providers, ProvidersStatus
from app.models.notification_core_db import ProvidersDBModel
from app.models.notification_core import ProviderModel

from app.utilities.crypto import Crypto


class ProvidersRepository:

    @classmethod
    async def _convert_provider_to_dict(cls, provider_from_db: ProvidersDBModel) -> dict:
        channel = provider_from_db.channel.value
        status = provider_from_db.status
        provider = await provider_from_db.to_dict()
        provider["created"] = int(provider["created"].timestamp())
        provider["updated"] = int(provider["updated"].timestamp())
        provider["configuration"] = await cls.decrypt_configuration(provider["configuration"])
        provider["channel"] = channel
        provider["status"] = status
        return provider

    @classmethod
    async def decrypt_configuration(cls, configuration: dict) -> dict:
        for key, val in configuration.items():
            if isinstance(val, str) or isinstance(val, int):
                configuration[key] = Crypto.decrypt(val)
            elif isinstance(val, dict):
                configuration[key] = await cls.decrypt_configuration(val)
        return configuration

    @classmethod
    async def encrypt_configuration(cls, configuration: dict) -> dict:
        for key, val in configuration.items():
            if isinstance(val, str):
                configuration[key] = Crypto.encrypt(val)
            elif isinstance(val, int):
                configuration[key] = Crypto.encrypt(str(val))
            elif isinstance(val, dict):
                val_copy = copy.deepcopy(val)
                enc_data = await cls.encrypt_configuration(val_copy)
                configuration[key] = enc_data
        return configuration

    @classmethod
    async def get_configured_providers(cls, limit=10, offset=0) -> list[ProviderModel]:
        select_filters = {}
        providers_rows = await ORMWrapper.get_by_filters(
            ProvidersDBModel, filters=select_filters, limit=limit, offset=offset, order_by="id",
        )
        providers = list()
        for row in providers_rows:
            provider_dict = await cls._convert_provider_to_dict(row)
            providers.append(ProviderModel(provider_dict))
        return providers

    @classmethod
    async def get_provider_by_unique_id(cls, unique_identifier: str) -> ProviderModel:
        select_filter = {
            "unique_identifier": unique_identifier
        }
        rows = await ORMWrapper.get_by_filters(ProvidersDBModel, select_filter)
        if rows:
            return ProviderModel(await cls._convert_provider_to_dict(rows[0]))
        raise NotFoundException("Provider not found")

    @classmethod
    async def get_providers_for_channel(
            cls, channel: NotificationChannels, include_disabled=False
    ) -> list[ProviderModel]:
        if include_disabled:
            select_filter = {
                "channel": channel.value
            }
        else:
            select_filter = {
                "channel": channel.value,
                "status": ProvidersStatus.ACTIVE.value
            }
        rows = await ORMWrapper.get_by_filters(ProvidersDBModel, select_filter)
        providers_list = list()
        for row in rows:
            providers_list.append(ProviderModel(await cls._convert_provider_to_dict(row)))
        return providers_list

    @classmethod
    async def total_count(cls):
        return await ORMWrapper.get_by_filters_count(ProvidersDBModel, filters={})


    @classmethod
    async def add_new_provider(
            cls,
            channel: NotificationChannels,
            provider: Providers,
            unique_identifier: str,
            configuration: dict
    ) -> ProviderModel:
        values = {
            "channel": channel.value,
            "provider": provider.value["code"],
            "unique_identifier": unique_identifier,
            "configuration": await cls.encrypt_configuration(configuration)
        }
        try:
            await ORMWrapper.create(ProvidersDBModel, values)
        except IntegrityError:
            raise BadRequestException("unique_identifier not available. Choose a different unique_identifier")
        return await cls.get_provider_by_unique_id(unique_identifier)

    @classmethod
    async def update_provider(cls, unique_identifier, disable=False, configuration=None) -> ProviderModel:
        values = {
            "status": ProvidersStatus.DISABLED.value if disable else ProvidersStatus.DISABLED.value
        }
        if configuration:
            values["configuration"] = await cls.encrypt_configuration(configuration)
        where_clause = {
            "unique_identifier": unique_identifier
        }
        await ORMWrapper.update_with_filters(None, ProvidersDBModel, values, where_clause=where_clause)
        return await cls.get_provider_by_unique_id(unique_identifier)
