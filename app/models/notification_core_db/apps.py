from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField
from app.models.base import BaseModel
from app.constants import DatabaseTables


class AppsDBModel(BaseModel):
    class Meta:
        table = DatabaseTables.APPS.value

    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    callback_url = fields.CharField(max_length=1000, null=True)
    callback_events = fields.JSONField(null=True)
    metadata = fields.JSONField(null=True)
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)
