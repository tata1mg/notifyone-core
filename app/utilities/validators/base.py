from commonutils.utils import CustomEnum

from app.exceptions import InvalidParamsException


def validate_enum_values(values: list, enum_class: CustomEnum, exec_class=InvalidParamsException):
    for val in values:
        if not enum_class.get_enum(val):
            raise exec_class("Invalid value {} for enum class {}".format(val, enum_class.__name__))
    return True
