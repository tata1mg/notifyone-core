from typing import Literal

from enum import Enum

_FieldType = Literal[
    "text",
    "number",
    "double",
    "float",
    "integer",
    "textarea",
    "select",
    "date_picker",
    "range_picker",
    "email",
    "url",
    "checkbox",
    "expression",
    "radio_group",
    "image_preview",
    "upload",
    "editor",
    "switch",
    "collection",
    "field_array",
    "dependent",
    "CUSTOM_PREVIEW_EMAIL",
    "CUSTOM_PREVIEW_SMS",
    "CUSTOM_PREVIEW_PUSH"
]


class FieldType(Enum):
    TEXT: _FieldType = "text"
    NUMBER: _FieldType = "number"
    DOUBLE: _FieldType = "double"
    FLOAT: _FieldType = "float"
    INTEGER: _FieldType = "integer"
    TEXTAREA: _FieldType = "textarea"
    SELECT: _FieldType = "select"
    DATE_PICKER: _FieldType = "date_picker"
    RANGE_PICKER: _FieldType = "range_picker"
    EMAIL: _FieldType = "email"
    URL: _FieldType = "url"
    CHECKBOX: _FieldType = "checkbox"
    EXPRESSION: _FieldType = "expression"
    RADIO_GROUP: _FieldType = "radio_group"
    IMAGE_PREVIEW: _FieldType = "image_preview"
    UPLOAD: _FieldType = "upload"
    EDITOR: _FieldType = "editor"
    SWITCH: _FieldType = "switch"
    COLLECTION: _FieldType = "collection"
    FIELD_ARRAY: _FieldType = "field_array"
    DEPENDENT: _FieldType = "dependent"
    CUSTOM_PREVIEW_EMAIL: _FieldType = "CUSTOM_PREVIEW_EMAIL"
    CUSTOM_PREVIEW_SMS: _FieldType = "CUSTOM_PREVIEW_SMS"
    CUSTOM_PREVIEW_PUSH: _FieldType = "CUSTOM_PREVIEW_PUSH"
