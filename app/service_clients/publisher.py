from typing import ClassVar, Dict, List, Optional

import abc
from dataclasses import dataclass

from app.constants import NotificationRequestLogStatus
from app.utilities.json_serializable_dataclass import JSONSerializableDataClass


@dataclass
class OperatorDetails(JSONSerializableDataClass):
    name: str
    event_id: Optional[str] = None


@dataclass
class PublishResult(JSONSerializableDataClass):
    __SERIALIZABLE_KEYS__: ClassVar[Optional[List[str]]] = [
        "is_success",
        "status",
        "message",
        "operator_details",
    ]

    is_success: bool
    status: NotificationRequestLogStatus
    unhandled_exception: bool = False
    message: str = ""
    operator_details: Optional[OperatorDetails] = None


class Publisher(abc.ABC):
    @abc.abstractmethod
    async def publish(self, data: Dict) -> PublishResult:
        raise NotImplementedError
