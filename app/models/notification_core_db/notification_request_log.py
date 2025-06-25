import enum

from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField

from app.models.base import BaseModel
from app.constants import DatabaseTables, NotificationRequestLogStatus



class NotificationRequestLogDBModel(BaseModel):

    class Meta:
        table = DatabaseTables.NOTIFICATION_REQUEST_LOG.value

    id: int = fields.BigIntField(pk=True)
    event_id = fields.BigIntField()
    content_length = fields.BigIntField()
    notification_request_id = fields.CharField(max_length=100)
    channel = fields.CharField(max_length=100)
    sent_to = fields.CharField(max_length=1000, null=True)
    source_identifier = fields.CharField(max_length=1000, null=True)
    status = fields.CharField(max_length=50, default=NotificationRequestLogStatus.NEW.value)
    operator = fields.CharField(max_length=50, null=True)
    operator_event_id = fields.CharField(max_length=1000, null=True)
    source = fields.CharField(max_length=50, default="UNKNOWN")
    channel_status = fields.CharField(max_length=50, default="UNKNOWN")
    message = fields.CharField(max_length=5000, null=True)
    metadata = fields.CharField(max_length=5000, null=True)
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)
