from app.services.form.fields import (
    Collection,
    CollapseContainerConfig,
    TextInput,
    NumberInput,
    CollapseConfig,
    SwtichField
)
from app.services.form.fields.field_rule import Required

class WhatsAppForm:
    def __init__(self, whatsapp_content, trigger_limit, enabled) -> None:
        self._whatsapp_content = whatsapp_content
        self._trigger_limit = trigger_limit if whatsapp_content.id else None
        self._enabled = bool(whatsapp_content.id and enabled)  

    def _get_components(self):
        return {
            "trigger_limit": NumberInput(
                name="trigger_limit",
                label="Trigger Limit",
                initialValue=self._trigger_limit,
                controls=False,
                span=12,
                tooltip="maximum number of times a particular event can be triggered for a particular order (set -1 for infinite times)",  # noqa
            ),
            "enabled": SwtichField(
                name="enabled",
                label="Enabled",
                initialValue=self._enabled,
                span=12,
            ),
            "name": TextInput(name="name", label="Name", initialValue=self._whatsapp_content.name),
        }

    def get(self):
        components = self._get_components()
        active_key = 0 if self._whatsapp_content.id else None
        return Collection(
            name="whatsapp",
            label="WhatsApp",
            order=[
                "trigger_limit",
                "enabled",
                "name",
            ],
            components=components,
            collapseContainerConfig=CollapseContainerConfig(
                canCollapse=True,
                collapseConfig=CollapseConfig(defaultActiveKey=active_key),
            ),
        )