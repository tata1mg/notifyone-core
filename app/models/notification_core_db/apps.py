from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField
from app.models.base import BaseModel
from app.constants import DatabaseTables


class AppsDBModel(BaseModel):
    class Meta:
        table = DatabaseTables.APPS.value

    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    info = fields.JSONField()
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)
