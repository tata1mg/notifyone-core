import re

from commonutils.utils import CustomEnum
from app.exceptions import InvalidParamsException


mobile_format = re.compile("""^(\+\d{1,3}[- ]?)?\d{10}$""")
email_format = re.compile(
            r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
            r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'
            r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,10}\.?$', re.IGNORECASE)


def validate_enum_values(values: list, enum_class: CustomEnum, exec_class=InvalidParamsException):
    for val in values:
        if not enum_class.get_enum(val):
            raise exec_class("Invalid value {} for enum class {}".format(val, enum_class.__name__))
    return True


def validate_email(email: str) -> bool:
    for email in email.split(','):
        if not email_format.match(email.strip()):
            return False
    return True


def validate_mobile(mobile: str) -> bool:
    if mobile_format.match(mobile):
        return True
    return False
