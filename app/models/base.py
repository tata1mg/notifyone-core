from tortoise import Model, fields
from tortoise_wrapper.db.mixins import ModelUtilMixin


class BaseModel(Model, ModelUtilMixin):

    pass