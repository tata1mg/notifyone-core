from enum import Enum
from typing import Any, List, Optional, Type
from dataclasses import dataclass, field

from .base import BaseField, FieldType
from app.services.form.enums import DataFetchMode, SelectMode

SearchDebounceTimeout = Any



@dataclass
class Option:
    value: str
    label: str

    @staticmethod
    def from_enum(enum: Enum):
        return [Option(value=item.value, label=item.name) for item in enum]


@dataclass
class SelectField(BaseField):
    type: FieldType = FieldType.SELECT
    options: List[Option] = field(default_factory=list)

    dataFetchMode: DataFetchMode = DataFetchMode.STATIC
    dataSourceUrl: Optional[str] = None

    debounceTimeout: Optional[Type[SearchDebounceTimeout]] = None

    showSearch: bool = False
    mode: Optional[SelectMode] = None
