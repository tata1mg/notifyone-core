from textwrap import dedent

from app.services.form.fields import (
    Collection,
    CollapseContainerConfig,
    TextInput,
    NumberInput,
    TextArea,
)
from app.services.form.fields.field_rule import Required


class SmsForm:
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
        }

    @classmethod
    def get(cls):
        components = cls._get_components()
        return Collection(
            name="sms",
            label="SMS",
            order=[
                "description",
                "trigger_limit",
                "content",
            ],
            components=components,
            collapseContainerConfig=CollapseContainerConfig(canCollapse=True),
            tooltip=dedent(
                """
                The following steps have to be performed in order to create a SMS
                    1. Get the DLT approval for the SMS template
                    2. Creating a new Event on notification system
                    3. Adding the template to Plivo and/or SMS Country

                For more information: https://1-mg.in/wxsO8EPvO
                """
            ),
        )
