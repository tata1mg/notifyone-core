from app.constants.push import DeviceType, PushTarget
from app.services.form.fields import (
    Collection,
    CollapseContainerConfig,
    TextInput,
    NumberInput,
    Option,
    SelectField,
)
from app.services.form.fields.field_rule import Required


class PushForm:
    @classmethod
    def __get_targets(cls):
        targets = []
        for target in PushTarget.TARGET.keys():
            targets.append(Option(value=target, label=target))

        # finally add DYNAMIC TARGET
        dynamic_target = PushTarget.DYNAMIC_TARGET.get("name")
        targets.append(Option(value=dynamic_target, label=dynamic_target))
        return targets

    @classmethod
    def _get_components(cls):
        return {
            "device_type": SelectField(
                name="device_type",
                label="Device Type",
                span=12,
                options=Option.from_enum(DeviceType),
            ),
            "trigger_limit": NumberInput(
                name="trigger_limit",
                label="Trigger Limit",
                span=12,
                rules=[Required],
                tooltip="maximum number of times a particular event can be triggered for a particular order (set -1 for infinite times)",  # noqa
            ),
            "title": TextInput(name="title", label="Title", rules=[Required]),
            "body": TextInput(name="body", label="Body", rules=[Required]),
            "target": SelectField(
                name="target",
                label="Target",
                rules=[Required],
                options=cls.__get_targets(),
                tooltip="the location of page which opens the notification is clicked",
            ),
            "image": TextInput(name="image", label="Image"),
        }

    @classmethod
    def get(cls):
        components = cls._get_components()
        return Collection(
            name="push",
            label="Push",
            order=[
                "device_type",
                "trigger_limit",
                "title",
                "body",
                "target",
                "image",
            ],
            components=components,
            collapseContainerConfig=CollapseContainerConfig(canCollapse=True),
        )
