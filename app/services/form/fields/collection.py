from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from .base import CollapsibleContainer, FieldType
from .field_types import AnyField


class CardType(Enum):
    INNER = "inner"
    NULL = None


@dataclass
class Collection(CollapsibleContainer):
    type: FieldType = FieldType.COLLECTION

    order: List[str] = field(default_factory=list)
    components: Dict[str, AnyField] = field(default_factory=dict)

    name: Optional[str] = None
    cardType: CardType = CardType.NULL
