
from dataclasses import dataclass
from .base import BaseField, FieldType


@dataclass
class CustomFieldEmail(BaseField):
    type: FieldType = FieldType.CUSTOM_PREVIEW_EMAIL
    custom: bool = True
    buttonType: str = "primary"


@dataclass
class CustomFieldSms(BaseField):
    type: FieldType = FieldType.CUSTOM_PREVIEW_SMS
    custom: bool = True
    buttonType: str = "primary"


@dataclass
class CustomFieldPush(BaseField):
    type: FieldType = FieldType.CUSTOM_PREVIEW_PUSH
    custom: bool = True
    buttonType: str = "primary"

