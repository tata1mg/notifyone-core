from typing import Union

from .input import EmailInput, NumberInput, TextInput, UrlInput
from .select import SelectField
from .switch import SwtichField
from .text_area import TextArea


AnyField = Union[
    EmailInput,
    NumberInput,
    TextInput,
    UrlInput,
    SelectField,
    SwtichField,
    TextArea,
]
