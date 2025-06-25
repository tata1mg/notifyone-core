from enum import Enum


class ExecutionDetailsSource(str, Enum):
    INTERNAL = "INTERNAL"
    WEBHOOK = "WEBHOOK"


class ExecutionDetailsEventStatus(str, Enum):
    QUEUED = "QUEUED"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
