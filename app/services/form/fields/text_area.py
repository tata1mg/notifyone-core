from dataclasses import dataclass

from .base import BaseField, FieldType, Number


@dataclass
class TextArea(BaseField):
    type: FieldType = FieldType.TEXTAREA
    placeholder: str = "..."
    rows: Number = 4
