from app.services.form.fields import (
    Collection,
    CollapseContainerConfig,
    TextInput,
    NumberInput,
)
from app.services.form.fields.field_rule import Required


class WhatsAppForm:
    @classmethod
    def _get_components(cls):
        return {
            "trigger_limit": NumberInput(
                name="trigger_limit",
                label="Trigger Limit",
                rules=[Required],
                tooltip="maximum number of times a particular event can be triggered for a particular order (set -1 for infinite times)",  # noqa
            ),
            "name": TextInput(name="name", label="Name", rules=[Required]),
        }

    @classmethod
    def get(cls):
        components = cls._get_components()
        return Collection(
            name="whatsapp",
            label="WhatsApp",
            order=[
                "trigger_limit",
                "name",
            ],
            components=components,
            collapseContainerConfig=CollapseContainerConfig(canCollapse=True),
        )
