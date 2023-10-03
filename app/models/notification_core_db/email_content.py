from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField
from app.models.base import BaseModel
from app.constants import DatabaseTables
from app.utilities import max_int

class EmailContentDBModel(BaseModel):
    class Meta:
        table = DatabaseTables.EMAIL_CONTENT.value

    id = fields.BigIntField(pk=True)
    event_id = fields.BigIntField(unique=True)
    subject = fields.TextField()
    content = fields.TextField()
    description = fields.TextField()
    name = fields.CharField(max_length=100, unique=True)
    path = fields.CharField(max_length=500)
    updated_by = fields.CharField(max_length=100)
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)
