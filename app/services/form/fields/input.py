from typing import ClassVar
from dataclasses import dataclass

from .base import BaseField, FieldType


@dataclass
class InputField(BaseField):
    placeholder: str = "..."


@dataclass
class TextInput(InputField):
    type: FieldType = FieldType.TEXT


@dataclass
class NumberInput(InputField):
    type: FieldType = FieldType.NUMBER


@dataclass
class EmailInput(InputField):
    type: FieldType = FieldType.EMAIL


class UrlInput(InputField):
    type: FieldType = FieldType.URL
