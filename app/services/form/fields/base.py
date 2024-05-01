from typing import Any, Dict, List, Optional, Union

from dataclasses import dataclass, field

from app.services.form.enums import Size, FieldType, FormLabelAlign
from app.services.form.fields.field_rule import FieldRule

Number = Union[int, float, complex]
FieldPath = Optional[List[str]]


@dataclass
class BaseConfig:
    name: str = "name"
    type: FieldType = field(init=False)
    label: Optional[str] = "Label"

    fieldKey: Optional[str] = None
    elementName: FieldPath = None
    absolutePath: FieldPath = None
    parentPath: FieldPath = None

    editable: bool = True
    bordered: bool = True
    disabled: bool = False
    size: Size = Size.MEDIUM
    tooltip: Optional[str] = None
    rules: Optional[List[FieldRule]] = None

    dependsOn: Optional[Union[List[str], List[List[str]]]] = None
    dependencyExpression: Optional[str] = None


@dataclass
class LabelCol:
    span: Optional[Number] = None
    offset: Optional[Number] = None


@dataclass
class WrapperCol:
    span: Optional[Number] = None
    offset: Optional[Number] = None


@dataclass
class BaseField(BaseConfig):
    newline: bool = False
    initialValue: Any = None

    offset: Number = 0
    span: Number = 24

    labelCol: Optional[LabelCol] = None
    wrapperCol: Optional[WrapperCol] = None
    labelAlign: Optional[FormLabelAlign] = None


BaseWrapper = BaseConfig


@dataclass
class CollapseContainerConfig:
    canCollapse: bool = True
    panelConfig: Dict = field(default_factory=dict)


@dataclass
class CollapsibleContainer(BaseWrapper):
    collapseContainerConfig: Optional[CollapseContainerConfig] = None
