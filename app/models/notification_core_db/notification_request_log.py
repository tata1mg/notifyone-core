import enum

from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField

from app.models.base import BaseModel
from app.constants import DatabaseTables, NotificationRequestLogStatus



class NotificationRequestLogDBModel(BaseModel):

    class Meta:
        table = DatabaseTables.NOTIFICATION_REQUEST_LOG.value
        indexes = (("source_identifier", "event_id",),)

    id: int = fields.BigIntField(pk=True)
    event_id = fields.BigIntField()
    notification_request_id = fields.CharField(max_length=100, index=True)
    channel = fields.CharField(max_length=100)
    sent_to = fields.CharField(max_length=1000, null=True, index=True)
    source_identifier = fields.CharField(max_length=1000, null=True, index=True)
    status = fields.CharEnumField(enum_type=NotificationRequestLogStatus, default=NotificationRequestLogStatus.NEW.value)
    operator = fields.CharField(max_length=50, null=True)
    operator_event_id = fields.CharField(max_length=200, null=True, index=True)
    message = fields.TextField(null=True)
    metadata = fields.TextField(null=True)
    created = NaiveDatetimeField(auto_now=True, index=True)
    updated = NaiveDatetimeField(auto_now=True)
