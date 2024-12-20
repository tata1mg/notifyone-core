from cloudinary.cache.responsive_breakpoints_cache import instance

from app.constants import NotificationChannels, Providers
from app.services.form.fields import (
    Collection,
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


class AddProviderForm(GenericForm):

    @classmethod
    async def __get_components_recursively(cls, configuration) -> dict:
        components = dict()
        for key, val in configuration.items():
            if isinstance(val, str):
                components[key] = TextInput(
                    name=key,
                    label=str(key).replace("_", " ")
                )
            elif isinstance(val, int):
                components[key] = NumberInput(
                    name=key,
                    label=str(key).replace("_", " ")
                )
            elif isinstance(val, dict):
                components[key] = Collection(
                    name=key,
                    label=str(key).replace("_", " "),
                    order=list(val.keys()),
                    components=await cls.__get_components_recursively(val),
                )
        return components

    @classmethod
    async def _get_components(cls, channel_enum: NotificationChannels, provider_enum: Providers):
        configuration = provider_enum.value["configuration"]
        return {
            "channel": TextInput(
                name="channel",
                label="Channel",
                initialValue=channel_enum.value,
                editable=False,
                disabled=True
            ),
            "provider": TextInput(
                name="provider",
                label="Provider",
                initialValue=provider_enum.value["code"],
                editable=False,
                disabled=True
            ),
            "unique_identifier": TextInput(
                name="unique_identifier",
                label="Unique Identifier",
                placeholder="A unique code for this provider configuration"
            ),
            "configuration": Collection(
                name="configuration",
                label="Provider Configuration",
                order=list(configuration.keys()),
                components=await cls.__get_components_recursively(configuration),
            )
        }

    @classmethod
    async def get_with_params(cls, **kwargs):
        channel_enum: NotificationChannels = kwargs.get("channel")
        provider_enum: Providers = kwargs.get("provider")

        components = await cls._get_components(channel_enum, provider_enum)
        return Collection(
            name="add_provider",
            label="Add Provider",
            order=[
                "channel",
                "provider",
                "unique_identifier",
                "configuration"
            ],
            components=components,
        )
