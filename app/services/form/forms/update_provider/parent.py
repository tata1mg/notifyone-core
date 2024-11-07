from cloudinary.cache.responsive_breakpoints_cache import instance
from pycparser.c_ast import Switch
from torpedo.exceptions import NotFoundException, BadRequestException

from app.constants import NotificationChannels, Providers, ProvidersStatus
from app.models.notification_core import ProviderModel
from app.repositories.providers import ProvidersRepository
from app.services.form.fields import (
    Collection,
    SwtichField,
    Option,
    SelectField,
    TextInput,
    UrlInput,
    EmailInput,
    NumberInput
)
from app.services.form import GenericForm
from app.services.form.fields.field_rule import Required
from app.repositories.apps import AppsRepository


class UpdateProviderForm(GenericForm):

    @classmethod
    async def __get_components_recursively(cls, configuration, saved_configuration) -> dict:
        components = dict()
        for key, val in configuration.items():
            if isinstance(val, str):
                components[key] = TextInput(
                    name=key,
                    label=str(key).replace("_", " "),
                    initialValue=saved_configuration[key]
                )
            elif instance(val, int):
                components[key] = NumberInput(
                    name=key,
                    label=str(key).replace("_", " "),
                    initialValue=saved_configuration[key]
                )
            elif instance(val, dict):
                components[key] = Collection(
                    name=key,
                    label=str(key).replace("_", " "),
                    order=list(val.keys()),
                    components=await cls.__get_components_recursively(val, saved_configuration[key]),
                )
        return components

    @classmethod
    async def _get_components(cls, provider_model: ProviderModel):
        configuration = Providers.get_enum_from_code(provider_model.provider).value["configuration"]
        return {
            "channel": TextInput(
                name="channel",
                label="Channel",
                initialValue=provider_model.channel,
                editable=False,
                disabled=True
            ),
            "provider": TextInput(
                name="provider",
                label="Provider",
                initialValue=provider_model.provider,
                editable=False,
                disabled=True
            ),
            "unique_identifier": TextInput(
                name="provider",
                label="Provider",
                initialValue=provider_model.unique_identifier,
                editable=False,
                disabled=True
            ),
            "enabled": SwtichField(
                name="enabled",
                label="Enable/Disable This Provider",
                initialValue=True if provider_model.status.value == ProvidersStatus.ACTIVE.value else False,
                span=12,
            ),
            "configuration": Collection(
                name="configuration",
                label="Provider Configuration",
                order=list(configuration.keys()),
                components=await cls.__get_components_recursively(configuration, provider_model.configuration),
            )
        }

    @classmethod
    async def get_instance(cls, unique_identifier: str):
        try:
            provider_model = await ProvidersRepository.get_provider_by_unique_id(unique_identifier)
        except NotFoundException:
            raise BadRequestException("No data found for unique id - {}".format(unique_identifier))
        components = await cls._get_components(provider_model)
        return Collection(
            name="update_provider",
            label="Update Provider",
            order=[
                "channel",
                "provider",
                "unique_identifier",
                "enabled",
                "configuration"
            ],
            components=components,
        )
