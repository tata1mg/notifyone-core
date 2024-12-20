from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField
from app.models.base import BaseModel
from app.constants import DatabaseTables, NotificationChannels, ProvidersDefaultPriorityStatus


class ProvidersDefaultPriorityDBModel(BaseModel):
    class Meta:
        table = DatabaseTables.PROVIDERS_DEFAULT_PRIORITY.value

    id = fields.BigIntField(pk=True)
    channel = fields.CharEnumField(enum_type=NotificationChannels, unique=True)
    priority = fields.JSONField()
    status = fields.CharEnumField(enum_type=ProvidersDefaultPriorityStatus, default=ProvidersDefaultPriorityStatus.ACTIVE.value)
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)
