from app.services.form.fields import (
    Collection,
    CollapseContainerConfig,
    TextInput,
    NumberInput,
    TextArea,
    CustomFieldEmail,
    CollapseConfig,
    SwtichField
)
from app.services.form.fields.field_rule import Required

class EmailForm:
    def __init__(self, email_content, trigger_limit, enabled) -> None:
        self._email_content = email_content
        self._trigger_limit = trigger_limit if email_content.id else None 
        self._enabled = bool(email_content.id and enabled)
    
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
                "description": TextInput(name="description", label="Description", initialValue=self._email_content.description),
                "subject": TextInput(name="subject", label="Subject", initialValue=self._email_content.subject),
                "content": TextArea(name="content", label="Content", initialValue=self._email_content.content),
                "preview": CustomFieldEmail(name="preview")
            }   

    def get(self):
        components = self._get_components()
        active_key = 0 if self._email_content.id else None
        return Collection(
            name="email",
            label="Email",
            order=["trigger_limit", "enabled", "description", "subject", "content", "preview"],
            components=components,
            collapseContainerConfig=CollapseContainerConfig(
                canCollapse=True,
                collapseConfig=CollapseConfig(defaultActiveKey=active_key),
            ),
        )    