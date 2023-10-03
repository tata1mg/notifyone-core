from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField
from app.models.base import BaseModel
from app.constants import DatabaseTables

class PushNotificationDBModel(BaseModel):
    class Meta:
        table = DatabaseTables.PUSH_NOTIFICATION.value

    id = fields.BigIntField(pk=True)
    event_id = fields.BigIntField(unique=True)
    title = fields.CharField(max_length=1000)
    body = fields.CharField(max_length=1000)
    target = fields.CharField(max_length=1000)
    image = fields.CharField(max_length=1000)
    device_type = fields.CharField(max_length=50)
    device_version = fields.CharField(max_length=50)
    updated_by = fields.CharField(max_length=100)
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)
