from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class Program:
    declarations: List[Any]


@dataclass
class StructDecl:
    name: str
    fields: List[Any]


@dataclass
class FunctionDecl:
    name: str
    params: List[Any]
    return_type: Optional[str]
    body: Any


@dataclass
class VarDecl:
    name: str
    type_name: str
    initializer: Optional[Any] = None


@dataclass
class Block:
    statements: List[Any]


@dataclass
class Assign:
    target: Any
    value: Any


@dataclass
class IfStmt:
    condition: Any
    then_branch: Any
    else_branch: Optional[Any] = None


@dataclass
class WhileStmt:
    condition: Any
    body: Any


@dataclass
class ReturnStmt:
    value: Optional[Any] = None


@dataclass
class PrintStmt:
    value: Any


@dataclass
class BreakStmt:
    pass


@dataclass
class ContinueStmt:
    pass


@dataclass
class ExprStmt:
    expression: Any


@dataclass
class Literal:
    value: Any


@dataclass
class Variable:
    name: str


@dataclass
class Binary:
    left: Any
    operator: str
    right: Any


@dataclass
class Unary:
    operator: str
    operand: Any


@dataclass
class Call:
    callee: Any
    arguments: List[Any]


@dataclass
class Member:
    object: Any
    name: str
