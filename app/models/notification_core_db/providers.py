from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField
from app.models.base import BaseModel
from app.constants import DatabaseTables, NotificationChannels, ProvidersStatus


class ProvidersDBModel(BaseModel):
    class Meta:
        table = DatabaseTables.PROVIDERS.value

    id = fields.BigIntField(pk=True)
    unique_identifier = fields.CharField(max_length=200, unique=True)
    provider = fields.TextField()
    channel = fields.CharEnumField(enum_type=NotificationChannels)
    status = fields.CharEnumField(enum_type=ProvidersStatus, default=ProvidersStatus.ACTIVE.value)
    configuration = fields.JSONField()
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)
