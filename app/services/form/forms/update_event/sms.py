from textwrap import dedent
from app.services.form.fields import (
    Collection,
    CollapseContainerConfig,
    TextInput,
    NumberInput,
    TextArea,
    CustomFieldSms,
    CollapseConfig,
    SwtichField
)
from app.services.form.fields.field_rule import Required

class SmsForm:
    def __init__(self, sms_content, trigger_limit, enabled) -> None:
        self._sms_content = sms_content
        self._trigger_limit = trigger_limit if sms_content.id else None
        self._enabled = bool(sms_content.id and enabled) 
        
    def _get_components(self):
        return {
            "trigger_limit": NumberInput(
                name="trigger_limit",
                label="Trigger Limit",
                initialValue = self._trigger_limit,
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
            "content": TextArea(name="content", label="Content", initialValue=self._sms_content.content),
            "preview": CustomFieldSms(name="preview")
        }
        
    def get(self):
        components = self._get_components()
        active_key = 0 if self._sms_content.id else None
        return Collection(
            name="sms",
            label="SMS",
            order=[
                "trigger_limit",
                "enabled",
                "content",
                "preview",
            ],
            components=components,
            collapseContainerConfig=CollapseContainerConfig(
                canCollapse=True,
                collapseConfig=CollapseConfig(defaultActiveKey=active_key),
            ),
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
