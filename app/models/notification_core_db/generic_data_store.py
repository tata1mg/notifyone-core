from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField
from app.models.base import BaseModel
from app.constants import DatabaseTables

class GenericDataStoreDBModel(BaseModel):
    class Meta:
        table = DatabaseTables.GENERIC_DATA_STORE.value
        unique_together = ("identifier", "category")

    id = fields.BigIntField(pk=True)
    category = fields.CharField(max_length=100)
    identifier = fields.CharField(max_length =1000)
    event_id = fields.BigIntField()
    data = fields.JSONField()
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)
    updated_by = fields.CharField(max_length=100)
  