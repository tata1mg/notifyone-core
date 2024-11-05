from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField
from app.models.base import BaseModel
from app.constants import DatabaseTables, NotificationChannels, ProvidersDynamicPriorityStatus


class ProvidersDynamicPriorityDBModel(BaseModel):
    class Meta:
        table = DatabaseTables.PROVIDERS_DYNAMIC_PRIORITY.value

    id = fields.BigIntField(pk=True)
    channel = fields.CharEnumField(enum_type=NotificationChannels, unique=True)
    priority_logic = fields.TextField(null=False)
    status = fields.CharEnumField(enum_type=ProvidersDynamicPriorityStatus, default=ProvidersDynamicPriorityStatus.ACTIVE.value)
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)
