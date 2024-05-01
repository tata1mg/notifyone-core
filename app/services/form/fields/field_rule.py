from dataclasses import dataclass


@dataclass
class FieldRule:
    required: bool = False
    message: str = "This is a FieldRule message"


Required = FieldRule(required=True, message="This is a required Field")
