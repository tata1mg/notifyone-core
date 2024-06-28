from commonutils.utils import CustomEnum


class EmailEventStatus(str, CustomEnum):
    OPENED = "OPENED"
    REJECTED = "REJECTED"
    SENT = "SENT"
    DEFERRED = "DEFERRED"
    DELIVERED = "DELIVERED"
    BOUNCED = "BOUNCED"
    CLICKED = "CLICKED"
    SPAM = "SPAM"
    UNSUBSCRIBED = "UNSUBSCRIBED"
    DELAYED = "DELAYED"
    COMPLAINT = "COMPLAINT"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return self.value


class SmsEventStatus(str, CustomEnum):
    SENT = "SENT"
    QUEUED = "QUEUED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    OPT_OUT = "OPT_OUT"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"
    DELIVERED = "DELIVERED"
    UNDELIVERED = "UNDELIVERED"
    INVALID_NUMBER = "INVALID_NUMBER"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return self.value


class PushEventStatus(str, CustomEnum):
    pass


class WhatsAppEventStatus(str, CustomEnum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return self.value
