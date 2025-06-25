from enum import Enum
from commonutils.utils import CustomEnum


class EventPriority(CustomEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @classmethod
    def _missing_(cls, _value):
        return cls.LOW


class EventType(Enum):
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    OTP = "otp"
