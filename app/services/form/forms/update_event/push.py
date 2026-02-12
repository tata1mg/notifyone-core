from app.constants.push import DeviceType, NotificationType, PushTarget
from app.services.form.fields import (
    Collection,
    CollapseContainerConfig,
    TextInput,
    NumberInput,
    Option,
    SelectField,
    CustomFieldPush,
    CollapseConfig,
    SwtichField,
)
from app.services.form.fields.field_rule import Required


class PushForm:
    def __init__(self, push_content, trigger_limit, enabled) -> None:
        self._push_content = push_content
        self._trigger_limit = trigger_limit if push_content.id else None
        self._enabled = bool(push_content.id and enabled)

    def __get_targets(self):
        targets = []
        for target in PushTarget.TARGET.keys():
            targets.append(Option(value=target, label=target))

        # finally add DYNAMIC TARGET
        dynamic_target = PushTarget.DYNAMIC_TARGET.get("name")
        targets.append(Option(value=dynamic_target, label=dynamic_target))
        return targets

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
            "device_type": SelectField(
                name="device_type",
                label="Device Type",
                initialValue=self._push_content.device_type,
                options=Option.from_enum(DeviceType),
            ),
            "type": SelectField(
                name="type",
                label="Type",
                span=12,
                initialValue=self._push_content.type,
                options=Option.from_enum(NotificationType),
            ),
            "title": TextInput(
                name="title", label="Title", initialValue=self._push_content.title
            ),
            "body": TextInput(
                name="body", label="Body", initialValue=self._push_content.body
            ),
            "target": SelectField(
                name="target",
                label="Target",
                initialValue=self._push_content.target,
                options=self.__get_targets(),
                tooltip="the location of page which opens the notification is clicked",
            ),
            "image": TextInput(
                name="image", label="Image", initialValue=self._push_content.image
            ),
            "preview": CustomFieldPush(name="preview"),
        }

    def get(self):
        components = self._get_components()
        active_key = 0 if self._push_content.id else None
        return Collection(
            name="push",
            label="Push",
            order=[
                "trigger_limit",
                "enabled",
                "device_type",
                "type",
                "title",
                "body",
                "target",
                "image",
                "preview",
            ],
            components=components,
            collapseContainerConfig=CollapseContainerConfig(
                canCollapse=True,
                collapseConfig=CollapseConfig(defaultActiveKey=active_key),
            ),
        )
