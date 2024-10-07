from pydantic import conint
from tortoise_wrapper.wrappers import ORMWrapper
from app.models.notification_core_db import ProvidersDBModel
from app.models.notification_core import ProviderModel

from app.utilities.crypto import Crypto


class ProvidersRepository:

    @classmethod
    async def _convert_provider_to_dict(cls, provider_from_db: ProvidersDBModel) -> dict:
        channel = provider_from_db.channel.value
        status = provider_from_db.status.value
        provider = await provider_from_db.to_dict()
        provider["created"] = int(provider["created"].timestamp())
        provider["updated"] = int(provider["updated"].timestamp())
        # provider["configuration"] = await cls.decrypt_configuration(provider["configuration"])
        provider["channel"] = channel
        provider["status"] = status
        return provider

    @classmethod
    async def decrypt_configuration(cls, configuration: dict) -> dict:
        for key, val in configuration.items():
            if isinstance(val, str) or isinstance(val, int):
                configuration[key] = Crypto.decrypt(val)
            elif isinstance(val, dict):
                configuration[key] = cls.decrypt_configuration(val)
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
    async def total_count(cls):
        return await ORMWrapper.get_by_filters_count(ProvidersDBModel, filters={})
