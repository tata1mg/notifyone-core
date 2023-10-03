from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField
from app.models.base import BaseModel
from app.constants import DatabaseTables


class EventDBModel(BaseModel):
    class Meta:
        table = DatabaseTables.EVENT.value
        unique_together = ("event_name", "app_name")

    id = fields.BigIntField(pk=True)
    event_name = fields.CharField(max_length=100)
    app_name = fields.CharField(max_length=100)
    actions = fields.JSONField()
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)
    subject = fields.CharField(max_length=100)
    updated_by = fields.CharField(max_length=100)
    event_type = fields.CharField(max_length=100)
    triggers_limit = fields.JSONField()
    meta_info = fields.JSONField()
    is_deleted = fields.BooleanField()
