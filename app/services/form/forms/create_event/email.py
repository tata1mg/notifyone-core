from app.services.form.fields import (
    Collection,
    CollapseContainerConfig,
    TextInput,
    NumberInput,
    TextArea,
)
from app.services.form.fields.field_rule import Required


class EmailForm:
    @classmethod
    def _get_components(cls):
        return {
            "description": TextInput(name="description", label="Description", span=12),
            "trigger_limit": NumberInput(
                name="trigger_limit",
                label="Trigger Limit",
                span=12,
                rules=[Required],
                tooltip="maximum number of times a particular event can be triggered for a particular order (set -1 for infinite times)",  # noqa
            ),
            "content": TextArea(name="content", label="Content", rules=[Required]),
            "subject": TextInput(name="subject", label="Subject", rules=[Required]),
        }

    @classmethod
    def get(cls):
        components = cls._get_components()
        return Collection(
            name="email",
            label="Email",
            order=[
                "description",
                "trigger_limit",
                "subject",
                "content",
            ],
            components=components,
            collapseContainerConfig=CollapseContainerConfig(canCollapse=True),
        )
