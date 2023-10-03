from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField

from app.models.base import BaseModel
from app.constants import DatabaseTables, NotificationRequestLogStatus


class NotificationRequestAttemptDBModel(BaseModel):
    class Meta:
        table = DatabaseTables.NOTIFICATION_REQUEST_ATTEMPT.value
        indexes = (("operator_event_id",), ("created",),)

    id: int = fields.BigIntField(pk=True)
    log_id: int = fields.BigIntField()
    channel = fields.CharField(max_length=100)
    sent_to = fields.CharField(max_length=5000, null=True)
    status = fields.CharField(
        max_length=50, default=NotificationRequestLogStatus.NEW.value
    )
    operator = fields.CharField(max_length=50, null=True)
    operator_event_id = fields.CharField(max_length=200, null=True)
    message = fields.CharField(max_length=5000, null=True)
    metadata = fields.CharField(max_length=5000, null=True)
    attempt_number = fields.IntField()
    sent_at = NaiveDatetimeField(auto_now=True)
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)
