"""Abstract Syntax Tree nodes for SQL queries."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass


class ASTNode(ABC):
    """Base class for all AST nodes."""

    @abstractmethod
    def accept(self, visitor: "ASTVisitor") -> Any:
        """Accept a visitor for traversal."""
        pass


class ASTVisitor(ABC):
    """Visitor pattern for AST traversal."""

    def visit_select_statement(self, node: "SelectStatement") -> Any:
        pass

    def visit_insert_statement(self, node: "InsertStatement") -> Any:
        pass

    def visit_update_statement(self, node: "UpdateStatement") -> Any:
        pass

    def visit_delete_statement(self, node: "DeleteStatement") -> Any:
        pass

    def visit_create_table_statement(self, node: "CreateTableStatement") -> Any:
        pass

    def visit_create_database_statement(self, node: "CreateDatabaseStatement") -> Any:
        pass

    def visit_drop_table_statement(self, node: "DropTableStatement") -> Any:
        pass

    def visit_drop_database_statement(self, node: "DropDatabaseStatement") -> Any:
        pass

    def visit_column_reference(self, node: "ColumnReference") -> Any:
        pass

    def visit_literal(self, node: "Literal") -> Any:
        pass

    def visit_binary_expression(self, node: "BinaryExpression") -> Any:
        pass

    def visit_unary_expression(self, node: "UnaryExpression") -> Any:
        pass

    def visit_function_call(self, node: "FunctionCall") -> Any:
        pass

    def visit_column_definition(self, node: "ColumnDefinition") -> Any:
        pass

    def visit_sql_statement(self, node: "SQLStatement") -> Any:
        pass


# Expression nodes
@dataclass
class ColumnReference(ASTNode):
    """Reference to a table column."""

    name: str
    table: Optional[str] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_column_reference(self)


@dataclass
class Literal(ASTNode):
    """Literal value (string, number, boolean, null)."""

    value: Any
    type: str  # 'string', 'number', 'boolean', 'null'

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_literal(self)


@dataclass
class BinaryExpression(ASTNode):
    """Binary expression (e.g., a = b, a + b)."""

    left: ASTNode
    operator: str
    right: ASTNode

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_binary_expression(self)


@dataclass
class UnaryExpression(ASTNode):
    """Unary expression (e.g., NOT condition)."""

    operator: str
    operand: ASTNode

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_unary_expression(self)


@dataclass
class FunctionCall(ASTNode):
    """Function call (e.g., COUNT(*), MAX(column))."""

    name: str
    arguments: List[ASTNode]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_function_call(self)


# Statement nodes
@dataclass
class SelectStatement(ASTNode):
    """SELECT statement."""

    columns: List[ASTNode]  # List of ColumnReference, Literal, or FunctionCall
    from_clause: Optional[str] = None  # Table name
    where_clause: Optional[ASTNode] = None  # Expression
    group_by: Optional[List[ColumnReference]] = None
    having: Optional[ASTNode] = None  # Expression
    order_by: Optional[
        List[tuple[ASTNode, str]]
    ] = None  # List of (ColumnReference, direction)
    limit: Optional[tuple[int, Optional[int]]] = None  # (limit, offset) tuple
    distinct: bool = False

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_select_statement(self)


@dataclass
class InsertStatement(ASTNode):
    """INSERT statement."""

    table: str
    values: List[List[ASTNode]]  # List of value lists
    columns: Optional[List[str]] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_insert_statement(self)


@dataclass
class UpdateStatement(ASTNode):
    """UPDATE statement."""

    table: str
    set_clause: Dict[str, ASTNode]  # column -> expression
    where_clause: Optional[ASTNode] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_update_statement(self)


@dataclass
class DeleteStatement(ASTNode):
    """DELETE statement."""

    table: str
    where_clause: Optional[ASTNode] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_delete_statement(self)


@dataclass
class ColumnDefinition(ASTNode):
    """Column definition in CREATE TABLE."""

    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    default_value: Optional[ASTNode] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_column_definition(self)


@dataclass
class CreateTableStatement(ASTNode):
    """CREATE TABLE statement."""

    table: str
    columns: List[ColumnDefinition]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_create_table_statement(self)


@dataclass
class CreateDatabaseStatement(ASTNode):
    """CREATE DATABASE statement."""

    database: str

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_create_database_statement(self)


@dataclass
class DropTableStatement(ASTNode):
    """DROP TABLE statement."""

    table: str

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_drop_table_statement(self)


@dataclass
class DropDatabaseStatement(ASTNode):
    """DROP DATABASE statement."""

    database: str

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_drop_database_statement(self)


# Root node
@dataclass
class SQLStatement(ASTNode):
    """Root node representing a complete SQL statement."""

    statement: ASTNode  # One of the statement types above

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_sql_statement(self)
