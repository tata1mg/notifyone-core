from tortoise import fields
from tortoise_wrapper.db.fields import NaiveDatetimeField
from app.models.base import BaseModel
from app.constants import DatabaseTables
from app.utilities import max_int

class WhatsappContentDBModel(BaseModel):
    class Meta:
        table = DatabaseTables.WHATSAPP_CONTENT.value

    id = fields.BigIntField(pk=True)
    event_id = fields.BigIntField(unique=True)
    name = fields.TextField()
    updated_by = fields.CharField(max_length=100)
    created = NaiveDatetimeField(auto_now=True)
    updated = NaiveDatetimeField(auto_now=True)