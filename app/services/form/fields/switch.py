from dataclasses import dataclass

from .base import BaseField, FieldType


@dataclass
class SwtichField(BaseField):
    type: FieldType = FieldType.SWITCH
    defaultChecked: bool = False
