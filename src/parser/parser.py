"""SQL parser using PLY (Python Lex-Yacc)."""

import ply.yacc as yacc
from typing import List, Optional, Dict, Any, Union, Callable
from .lexer import tokens, lexer
from .ast import (
    SelectStatement,
    InsertStatement,
    UpdateStatement,
    DeleteStatement,
    CreateTableStatement,
    CreateDatabaseStatement,
    DropTableStatement,
    DropDatabaseStatement,
    ColumnReference,
    Literal,
    BinaryExpression,
    UnaryExpression,
    ColumnDefinition,
    SQLStatement,
    FunctionCall,
)
from ..common.errors import ParserError
import logging
from graphviz import Digraph
from ..common import config
import uuid

# Get module-specific logger
from ..common.logging_config import get_logger

logger = get_logger("parser")


# Parser rules
def p_statement(p: Any) -> None:
    """statement : sql_statement SEMICOLON
    | sql_statement"""
    if len(p) == 3:
        logger.debug("p_statement: sql_statement SEMICOLON")
        p[0] = SQLStatement(statement=p[1])
    elif len(p) == 2:
        logger.debug("p_statement: sql_statement")
        p[0] = SQLStatement(statement=p[1])
    else:
        logger.error(f"p_statement: unexpected len(p)={len(p)}")
        p[0] = None


def p_sql_statement(p: Any) -> None:
    """sql_statement : select_statement
    | insert_statement
    | update_statement
    | delete_statement
    | create_statement
    | drop_statement"""
    if len(p) == 2:
        logger.debug("p_sql_statement: valid")
        p[0] = p[1]
    else:
        logger.error(f"p_sql_statement: unexpected len(p)={len(p)}")
        p[0] = None


def p_select_statement(p: Any) -> None:
    """select_statement : SELECT DISTINCT column_list FROM table_reference where_clause_opt group_by_opt having_opt order_by_opt limit_opt
    | SELECT column_list FROM table_reference where_clause_opt group_by_opt having_opt order_by_opt limit_opt
    """
    if len(p) == 10:
        logger.debug("p_select_statement: SELECT ...")
        p[0] = SelectStatement(
            columns=p[2],
            from_clause=p[4],
            where_clause=p[5],
            group_by=p[6],
            having=p[7],
            order_by=p[8],
            limit=p[9],
            distinct=False,
        )
    elif len(p) == 11:
        logger.debug("p_select_statement: SELECT DISTINCT ...")
        p[0] = SelectStatement(
            columns=p[3],
            from_clause=p[5],
            where_clause=p[6],
            group_by=p[7],
            having=p[8],
            order_by=p[9],
            limit=p[10],
            distinct=True,
        )
    else:
        logger.error(f"p_select_statement: unexpected len(p)={len(p)}")
        p[0] = None


def p_table_reference(p: Any) -> None:
    """table_reference : IDENTIFIER
    | IDENTIFIER AS IDENTIFIER
    | IDENTIFIER IDENTIFIER"""
    if len(p) == 2:
        logger.debug("p_table_reference: IDENTIFIER")
        p[0] = p[1]
    elif len(p) == 4:
        logger.debug("p_table_reference: IDENTIFIER AS IDENTIFIER")
        p[0] = f"{p[1]} AS {p[3]}"
    elif len(p) == 3:
        logger.debug("p_table_reference: IDENTIFIER IDENTIFIER")
        p[0] = f"{p[1]} {p[2]}"
    else:
        logger.error(f"p_table_reference: unexpected len(p)={len(p)}")
        p[0] = None


def p_column_list(p: Any) -> None:
    """column_list : ASTERISK
    | column_expression_list"""
    if len(p) == 2:
        # Check if p[1] is "*" (ASTERISK) or a column expression list
        if p[1] == "*":
            logger.debug("p_column_list: ASTERISK")
            p[0] = [ColumnReference(name="*")]
        else:
            logger.debug("p_column_list: column_expression_list")
            p[0] = p[1]
    else:
        logger.error(f"p_column_list: unexpected len(p)={len(p)}")
        p[0] = None


def p_column_expression_list(p: Any) -> None:
    """column_expression_list : column_expression
    | column_expression_list COMMA column_expression"""
    if len(p) == 2:
        logger.debug("p_column_expression_list: column_expression")
        p[0] = [p[1]]
    elif len(p) == 4:
        logger.debug(
            "p_column_expression_list: column_expression_list COMMA column_expression"
        )
        p[0] = p[1] + [p[3]]
    else:
        logger.error(f"p_column_expression_list: unexpected len(p)={len(p)}")
        p[0] = None


def p_column_expression(p: Any) -> None:
    """column_expression : column_reference
    | function_call
    | STRING_LITERAL
    | NUMBER_LITERAL
    | BOOLEAN_LITERAL
    | arithmetic_expression"""
    # arithmetic_expression is a new rule for arithmetic only, not full expression
    # This avoids cyclic reference with expression
    if len(p) == 2:
        # Check the type of p[1] to determine which alternative was matched
        if isinstance(p[1], str) and p[1].startswith("'") and p[1].endswith("'"):
            logger.debug(f"p_column_expression: STRING_LITERAL {p[1]}")
            p[0] = Literal(value=p[1], type="string")
        elif isinstance(p[1], bool):
            logger.debug(f"p_column_expression: BOOLEAN_LITERAL {p[1]}")
            p[0] = Literal(value=p[1], type="boolean")
        elif isinstance(p[1], (int, float)):
            logger.debug(f"p_column_expression: NUMBER_LITERAL {p[1]}")
            p[0] = Literal(value=p[1], type="number")
        elif (
            hasattr(p[1], "__class__") and p[1].__class__.__name__ == "ColumnReference"
        ):
            logger.debug(f"p_column_expression: column_reference {p[1]}")
            p[0] = p[1]
        elif hasattr(p[1], "__class__") and p[1].__class__.__name__ == "FunctionCall":
            logger.debug(f"p_column_expression: function_call {p[1]}")
            p[0] = p[1]
        elif hasattr(p[1], "__class__") and p[1].__class__.__name__ == "Literal":
            logger.debug(f"p_column_expression: propagate Literal {p[1]}")
            p[0] = p[1]
        elif (
            hasattr(p[1], "__class__") and p[1].__class__.__name__ == "BinaryExpression"
        ):
            logger.debug(f"p_column_expression: propagate BinaryExpression {p[1]}")
            p[0] = p[1]
        else:
            logger.debug(f"p_column_expression: fallback to string literal {p[1]}")
            p[0] = Literal(value=p[1], type="string")
    else:
        logger.error(f"p_column_expression: unexpected len(p)={len(p)}")
        p[0] = None


def p_arithmetic_expression(p: Any) -> None:
    """arithmetic_expression : primary_expression PLUS primary_expression
    | primary_expression MINUS primary_expression
    | primary_expression ASTERISK primary_expression
    | primary_expression DIVIDE primary_expression
    | LEFT_PAREN arithmetic_expression RIGHT_PAREN
    | NUMBER_LITERAL
    | STRING_LITERAL
    | BOOLEAN_LITERAL
    | NULL
    | column_reference
    | function_call"""
    # This rule allows arithmetic and function calls, but not full logical expressions
    if len(p) == 2:
        logger.debug("p_arithmetic_expression: single operand or literal")
        if p[1] == "NULL":
            p[0] = Literal(value=None, type="null")
        elif isinstance(p[1], str) and p[1].startswith("'") and p[1].endswith("'"):
            p[0] = Literal(value=p[1], type="string")
        elif type(p[1]) is int or type(p[1]) is float:
            p[0] = Literal(value=p[1], type="number")
        elif type(p[1]) is bool:
            p[0] = Literal(value=p[1], type="boolean")
        else:
            p[0] = p[1]
    elif len(p) == 4:
        if p[2] in ("+", "-", "*", "/"):
            logger.debug(f"p_arithmetic_expression: {p[1]} {p[2]} {p[3]}")
            p[0] = BinaryExpression(left=p[1], operator=p[2], right=p[3])
        elif p[1] == "(":
            logger.debug("p_arithmetic_expression: parenthesized expression")
            p[0] = p[2]
        else:
            logger.error(
                f"p_arithmetic_expression: unexpected tokens {p[1]}, {p[2]}, {p[3]}"
            )
            p[0] = None
    else:
        logger.error(f"p_arithmetic_expression: unexpected len(p)={len(p)}")
        p[0] = None


def p_function_call(p: Any) -> None:
    """function_call : IDENTIFIER LEFT_PAREN argument_list RIGHT_PAREN
    | COUNT LEFT_PAREN ASTERISK RIGHT_PAREN
    | COUNT LEFT_PAREN column_reference RIGHT_PAREN
    | SUM LEFT_PAREN column_reference RIGHT_PAREN
    | AVG LEFT_PAREN column_reference RIGHT_PAREN
    | MAX LEFT_PAREN column_reference RIGHT_PAREN
    | MIN LEFT_PAREN column_reference RIGHT_PAREN"""
    if (
        len(p) == 5
        and isinstance(p[1], str)
        and p[1].upper() not in ("COUNT", "SUM", "AVG", "MAX", "MIN")
    ):
        logger.debug(f"p_function_call: scalar function {p[1]} with arguments")
        p[0] = FunctionCall(name=p[1].lower(), arguments=p[3])
    elif len(p) == 5:
        logger.debug("p_function_call: valid aggregate function")
        if p[3] == "*":
            p[0] = FunctionCall(
                name=p[1].lower(), arguments=[ColumnReference(name="*")]
            )
        else:
            p[0] = FunctionCall(name=p[1].lower(), arguments=[p[3]])
    else:
        logger.error(f"p_function_call: unexpected len(p)={len(p)}")
        p[0] = None


def p_argument_list(p: Any) -> None:
    """argument_list : expression
    | argument_list COMMA expression"""
    if len(p) == 2:
        logger.debug("p_argument_list: single expression")
        p[0] = [p[1]]
    elif len(p) == 4:
        logger.debug("p_argument_list: argument_list COMMA expression")
        p[0] = p[1] + [p[3]]
    else:
        logger.error(f"p_argument_list: unexpected len(p)={len(p)}")
        p[0] = None


def p_column_reference(p: Any) -> None:
    """column_reference : IDENTIFIER
    | IDENTIFIER PERIOD IDENTIFIER"""
    if len(p) == 2:
        logger.debug("p_column_reference: IDENTIFIER")
        p[0] = ColumnReference(name=p[1])
    elif len(p) == 4:
        logger.debug("p_column_reference: IDENTIFIER PERIOD IDENTIFIER")
        p[0] = ColumnReference(name=p[3], table=p[1])
    else:
        logger.error(f"p_column_reference: unexpected len(p)={len(p)}")
        p[0] = None


def p_where_clause_opt(p: Any) -> None:
    """where_clause_opt : WHERE expression
    | empty"""
    if len(p) == 3:
        logger.debug("p_where_clause_opt: WHERE expression")
        p[0] = p[2]
    elif len(p) == 2:
        logger.debug("p_where_clause_opt: empty")
        p[0] = None
    else:
        logger.error(f"p_where_clause_opt: unexpected len(p)={len(p)}")
        p[0] = None


def p_group_by_opt(p: Any) -> None:
    """group_by_opt : GROUP BY column_reference_list
    | empty"""
    if len(p) == 4:
        logger.debug("p_group_by_opt: GROUP BY column_reference_list")
        p[0] = p[3]
    elif len(p) == 2:
        logger.debug("p_group_by_opt: empty")
        p[0] = None
    else:
        logger.error(f"p_group_by_opt: unexpected len(p)={len(p)}")
        p[0] = None


def p_column_reference_list(p: Any) -> None:
    """column_reference_list : column_reference
    | column_reference_list COMMA column_reference"""
    if len(p) == 2:
        logger.debug("p_column_reference_list: column_reference")
        p[0] = [p[1]]
    elif len(p) == 4:
        logger.debug(
            "p_column_reference_list: column_reference_list COMMA column_reference"
        )
        p[0] = p[1] + [p[3]]
    else:
        logger.error(f"p_column_reference_list: unexpected len(p)={len(p)}")
        p[0] = None


def p_having_opt(p: Any) -> None:
    """having_opt : HAVING expression
    | empty"""
    if len(p) == 3:
        logger.debug("p_having_opt: HAVING expression")
        p[0] = p[2]
    elif len(p) == 2:
        logger.debug("p_having_opt: empty")
        p[0] = None
    else:
        logger.error(f"p_having_opt: unexpected len(p)={len(p)}")
        p[0] = None


def p_order_by_opt(p: Any) -> None:
    """order_by_opt : ORDER BY order_item_list
    | empty"""
    if len(p) == 4:
        logger.debug("p_order_by_opt: ORDER BY order_item_list")
        p[0] = p[3]
    elif len(p) == 2:
        logger.debug("p_order_by_opt: empty")
        p[0] = None
    else:
        logger.error(f"p_order_by_opt: unexpected len(p)={len(p)}")
        p[0] = None


def p_order_item_list(p: Any) -> None:
    """order_item_list : order_item
    | order_item_list COMMA order_item"""
    if len(p) == 2:
        logger.debug("p_order_item_list: order_item")
        p[0] = [p[1]]
    elif len(p) == 4:
        logger.debug("p_order_item_list: order_item_list COMMA order_item")
        p[0] = p[1] + [p[3]]
    else:
        logger.error(f"p_order_item_list: unexpected len(p)={len(p)}")
        p[0] = None


def p_order_item(p: Any) -> None:
    """order_item : column_reference
    | column_reference ASC
    | column_reference DESC"""
    if len(p) == 2:
        logger.debug("p_order_item: column_reference")
        p[0] = (p[1], None)
    elif len(p) == 3 and p[2].upper() in ("ASC", "DESC"):
        logger.debug(f"p_order_item: column_reference {p[2].upper()}")
        p[0] = (p[1], p[2].upper())
    else:
        logger.debug(f"p_order_item: unexpected len(p)={len(p)}")
        p[0] = None


def p_limit_opt(p: Any) -> None:
    """limit_opt : LIMIT NUMBER_LITERAL
    | LIMIT NUMBER_LITERAL OFFSET NUMBER_LITERAL
    | empty"""
    if len(p) == 3:
        logger.debug("p_limit_opt: LIMIT NUMBER_LITERAL")
        p[0] = (int(p[2]), None)
    elif len(p) == 5:
        logger.debug("p_limit_opt: LIMIT NUMBER_LITERAL OFFSET NUMBER_LITERAL")
        p[0] = (int(p[2]), int(p[4]))
    elif len(p) == 2:
        logger.debug("p_limit_opt: empty")
        p[0] = (None, None)
    else:
        logger.debug(f"p_limit_opt: unexpected len(p)={len(p)}")
        p[0] = (None, None)


def p_insert_statement(p: Any) -> None:
    """insert_statement : INSERT INTO IDENTIFIER column_list_opt VALUES values_list"""
    if len(p) == 7:
        logger.debug("p_insert_statement: valid")
        p[0] = InsertStatement(table=p[3], columns=p[4], values=p[6])
    else:
        logger.debug(f"p_insert_statement: unexpected len(p)={len(p)}")
        p[0] = None


def p_column_list_opt(p: Any) -> None:
    """column_list_opt : LEFT_PAREN identifier_list RIGHT_PAREN
    | empty"""
    if len(p) == 4:
        logger.debug("p_column_list_opt: LEFT_PAREN identifier_list RIGHT_PAREN")
        p[0] = p[2]
    elif len(p) == 2:
        logger.debug("p_column_list_opt: empty")
        p[0] = None
    else:
        logger.debug(f"p_column_list_opt: unexpected len(p)={len(p)}")
        p[0] = None


def p_identifier_list(p: Any) -> None:
    """identifier_list : IDENTIFIER
    | identifier_list COMMA IDENTIFIER"""
    if len(p) == 2:
        logger.debug("p_identifier_list: IDENTIFIER")
        p[0] = [p[1]]
    elif len(p) == 4:
        logger.debug("p_identifier_list: identifier_list COMMA IDENTIFIER")
        p[0] = p[1] + [p[3]]
    else:
        logger.debug(f"p_identifier_list: unexpected len(p)={len(p)}")
        p[0] = None


def p_values_list(p: Any) -> None:
    """values_list : LEFT_PAREN value_list RIGHT_PAREN
    | values_list COMMA LEFT_PAREN value_list RIGHT_PAREN"""
    if len(p) == 4:
        logger.debug("p_values_list: LEFT_PAREN value_list RIGHT_PAREN")
        p[0] = [p[2]]
    elif len(p) == 6:
        logger.debug(
            "p_values_list: values_list COMMA LEFT_PAREN value_list RIGHT_PAREN"
        )
        p[0] = p[1] + [p[4]]
    else:
        logger.debug(f"p_values_list: unexpected len(p)={len(p)}")
        p[0] = None


def p_value_list(p: Any) -> None:
    """value_list : column_expression
    | value_list COMMA column_expression"""
    if len(p) == 2:
        logger.debug("p_value_list: column_expression")
        p[0] = [p[1]]
    elif len(p) == 4:
        logger.debug("p_value_list: value_list COMMA column_expression")
        p[0] = p[1] + [p[3]]
    else:
        logger.debug(f"p_value_list: unexpected len(p)={len(p)}")
        p[0] = None


def p_update_statement(p: Any) -> None:
    """update_statement : UPDATE IDENTIFIER SET set_clause where_clause_opt"""
    if len(p) == 6:
        logger.debug("p_update_statement: valid")
        p[0] = UpdateStatement(table=p[2], set_clause=p[4], where_clause=p[5])
    else:
        logger.debug(f"p_update_statement: unexpected len(p)={len(p)}")
        p[0] = None


def p_set_clause(p: Any) -> None:
    """set_clause : IDENTIFIER EQUALS expression
    | set_clause COMMA IDENTIFIER EQUALS expression"""
    if len(p) == 4 and p[2] == "=":
        logger.debug("p_set_clause: IDENTIFIER EQUALS expression")
        p[0] = {p[1]: p[3]}
    elif len(p) == 6 and p[3] and p[4] == "=":
        logger.debug("p_set_clause: set_clause COMMA IDENTIFIER EQUALS expression")
        p[0] = p[1]
        p[0][p[3]] = p[5]
    else:
        logger.debug(f"p_set_clause: unexpected len(p)={len(p)}")
        p[0] = None


def p_delete_statement(p: Any) -> None:
    """delete_statement : DELETE FROM IDENTIFIER where_clause_opt"""
    if len(p) == 5:
        logger.debug("p_delete_statement: valid")
        p[0] = DeleteStatement(table=p[3], where_clause=p[4])
    else:
        logger.debug(f"p_delete_statement: unexpected len(p)={len(p)}")
        p[0] = None


def p_create_statement(p: Any) -> None:
    """create_statement : CREATE TABLE IDENTIFIER LEFT_PAREN column_definition_list RIGHT_PAREN
    | CREATE DATABASE IDENTIFIER"""
    if len(p) == 7:
        logger.debug("p_create_statement: CREATE TABLE ...")
        p[0] = CreateTableStatement(table=p[3], columns=p[5])
    elif len(p) == 4:
        logger.debug("p_create_statement: CREATE DATABASE ...")
        p[0] = CreateDatabaseStatement(database=p[3])
    else:
        logger.debug(f"p_create_statement: unexpected len(p)={len(p)}")
        p[0] = None


def p_column_definition_list(p: Any) -> None:
    """column_definition_list : column_definition
    | column_definition_list COMMA column_definition"""
    if len(p) == 2:
        logger.debug("p_column_definition_list: column_definition")
        p[0] = [p[1]]
    elif len(p) == 4:
        logger.debug(
            "p_column_definition_list: column_definition_list COMMA column_definition"
        )
        p[0] = p[1] + [p[3]]
    else:
        logger.debug(f"p_column_definition_list: unexpected len(p)={len(p)}")
        p[0] = None


def p_column_definition(p: Any) -> None:
    """column_definition : IDENTIFIER data_type constraint_list_opt"""
    if len(p) == 4:
        logger.debug("p_column_definition: valid")
        p[0] = ColumnDefinition(
            name=p[1],
            data_type=p[2],
            nullable=p[3].get("nullable", True),
            primary_key=p[3].get("primary_key", False),
            default_value=p[3].get("default", None),
        )
    else:
        logger.debug(f"p_column_definition: unexpected len(p)={len(p)}")
        p[0] = None


def p_data_type(p: Any) -> None:
    """data_type : INTEGER
    | VARCHAR LEFT_PAREN NUMBER_LITERAL RIGHT_PAREN
    | CHAR LEFT_PAREN NUMBER_LITERAL RIGHT_PAREN
    | BOOLEAN
    | FLOAT
    | DOUBLE
    | DATE
    | TIMESTAMP
    | TEXT
    | BLOB"""
    if len(p) == 2:
        logger.debug("p_data_type: simple type")
        p[0] = p[1].lower()
    elif len(p) == 5:
        logger.debug("p_data_type: type with length")
        p[0] = f"{p[1].lower()}({p[3]})"
    else:
        logger.debug(f"p_data_type: unexpected len(p)={len(p)}")
        p[0] = None


def p_constraint_list_opt(p: Any) -> None:
    """constraint_list_opt : constraint_list
    | empty"""
    if len(p) == 2:
        # Check if p[1] is the empty sentinel or a constraint list
        if p[1] == "EMPTY_SENTINEL":
            logger.debug("p_constraint_list_opt: empty")
            p[0] = {}
        else:
            logger.debug("p_constraint_list_opt: constraint_list")
            p[0] = p[1]
    else:
        logger.debug(f"p_constraint_list_opt: unexpected len(p)={len(p)}")
        p[0] = None


def p_constraint_list(p: Any) -> None:
    """constraint_list : constraint
    | constraint_list constraint"""
    if len(p) == 2:
        logger.debug("p_constraint_list: constraint")
        p[0] = p[1]
        logger.debug(f"p_constraint_list: {p[0]}")
    elif len(p) == 3:
        logger.debug("p_constraint_list: constraint_list constraint")
        p[0] = {**p[1], **p[2]}
        logger.debug(f"p_constraint_list: {p[0]}")
    else:
        logger.debug(f"p_constraint_list: unexpected len(p)={len(p)}")
        p[0] = None


def p_constraint(p: Any) -> None:
    """constraint : PRIMARY KEY
    | NOT NULL
    | NULL"""
    if len(p) == 3:
        # Check which 3-token constraint was matched
        if p[1].upper() == "PRIMARY":
            logger.debug("p_constraint: PRIMARY KEY")
            p[0] = {"primary_key": True}
        elif p[1].upper() == "NOT":
            logger.debug("p_constraint: NOT NULL")
            p[0] = {"nullable": False}
        else:
            logger.debug(f"p_constraint: unexpected len(p)={len(p)}")
            p[0] = None
    elif len(p) == 2:
        if p[1].upper() == "NULL":
            logger.debug("p_constraint: NULL")
            p[0] = {"nullable": True}
        else:
            logger.debug(f"p_constraint: unexpected len(p)={len(p)}")
            p[0] = None
    else:
        logger.debug(f"p_constraint: unexpected len(p)={len(p)}")
        p[0] = None


def p_drop_statement(p: Any) -> None:
    """drop_statement : DROP TABLE IDENTIFIER
    | DROP DATABASE IDENTIFIER"""
    if len(p) == 4:
        # Check which DROP statement was matched
        if p[2].upper() == "TABLE":
            logger.debug("p_drop_statement: DROP TABLE IDENTIFIER")
            p[0] = DropTableStatement(table=p[3])
        elif p[2].upper() == "DATABASE":
            logger.debug("p_drop_statement: DROP DATABASE IDENTIFIER")
            p[0] = DropDatabaseStatement(database=p[3])
        else:
            logger.debug(f"p_drop_statement: unexpected len(p)={len(p)}")
            p[0] = None
    else:
        logger.debug(f"p_drop_statement: unexpected len(p)={len(p)}")
        p[0] = None


def p_expression(p: Any) -> None:
    """expression : or_expression"""
    if len(p) == 2:
        logger.debug("p_expression: or_expression")
        p[0] = p[1]
    else:
        logger.debug(f"p_expression: unexpected len(p)={len(p)}")
        p[0] = None


def p_or_expression(p: Any) -> None:
    """or_expression : and_expression
    | or_expression OR and_expression"""
    if len(p) == 2:
        logger.debug("p_or_expression: and_expression")
        p[0] = p[1]
    elif len(p) == 4:
        logger.debug("p_or_expression: or_expression OR and_expression")
        p[0] = BinaryExpression(left=p[1], operator="OR", right=p[3])
    else:
        logger.debug(f"p_or_expression: unexpected len(p)={len(p)}")
        p[0] = None


def p_and_expression(p: Any) -> None:
    """and_expression : equality_expression
    | and_expression AND equality_expression"""
    if len(p) == 2:
        logger.debug("p_and_expression: equality_expression")
        p[0] = p[1]
    elif len(p) == 4:
        logger.debug("p_and_expression: and_expression AND equality_expression")
        p[0] = BinaryExpression(left=p[1], operator="AND", right=p[3])
    else:
        logger.debug(f"p_and_expression: unexpected len(p)={len(p)}")
        p[0] = None


def p_equality_expression(p: Any) -> None:
    """equality_expression : comparison_expression
    | equality_expression EQUALS comparison_expression
    | equality_expression NOT_EQUALS comparison_expression
    | equality_expression IS NULL
    | equality_expression IS NOT NULL"""
    if len(p) == 2:
        logger.debug("p_equality_expression: comparison_expression")
        p[0] = p[1]
    elif len(p) == 4:
        # Check which 4-token expression was matched
        if p[2] in ("=", "!="):
            logger.debug(
                f"p_equality_expression: equality_expression {p[2]} comparison_expression"
            )
            p[0] = BinaryExpression(left=p[1], operator=p[2], right=p[3])
        elif p[2].upper() == "IS":
            logger.debug("p_equality_expression: equality_expression IS NULL")
            p[0] = BinaryExpression(
                left=p[1], operator="IS NULL", right=Literal(value=None, type="null")
            )
        else:
            logger.debug(f"p_equality_expression: unexpected len(p)={len(p)}")
            p[0] = None
    elif len(p) == 5:
        if p[2].upper() == "IS" and p[3].upper() == "NOT":
            logger.debug("p_equality_expression: equality_expression IS NOT NULL")
            p[0] = BinaryExpression(
                left=p[1],
                operator="IS NOT NULL",
                right=Literal(value=None, type="null"),
            )
        else:
            logger.debug(f"p_equality_expression: unexpected len(p)={len(p)}")
            p[0] = None
    else:
        logger.debug(f"p_equality_expression: unexpected len(p)={len(p)}")
        p[0] = None


def p_comparison_expression(p: Any) -> None:
    """comparison_expression : primary_expression
    | comparison_expression LESS_THAN primary_expression
    | comparison_expression LESS_EQUAL primary_expression
    | comparison_expression GREATER_THAN primary_expression
    | comparison_expression GREATER_EQUAL primary_expression
    | comparison_expression LIKE STRING_LITERAL
    | comparison_expression IN LEFT_PAREN value_list RIGHT_PAREN"""
    if len(p) == 2:
        logger.debug("p_comparison_expression: primary_expression")
        p[0] = p[1]
    elif len(p) == 4:
        # Check which 4-token expression was matched
        if p[2] in ("<", "<=", ">", ">="):
            logger.debug(
                f"p_comparison_expression: comparison_expression {p[2]} primary_expression"
            )
            p[0] = BinaryExpression(left=p[1], operator=p[2], right=p[3])
        elif p[2].upper() == "LIKE":
            logger.debug(
                "p_comparison_expression: comparison_expression LIKE STRING_LITERAL"
            )
            p[0] = BinaryExpression(
                left=p[1], operator="LIKE", right=Literal(value=p[3], type="string")
            )
        else:
            logger.debug(f"p_comparison_expression: unexpected len(p)={len(p)}")
            p[0] = None
    elif len(p) == 6:
        if p[2].upper() == "IN":
            logger.debug(
                "p_comparison_expression: comparison_expression IN LEFT_PAREN value_list RIGHT_PAREN"
            )
            p[0] = BinaryExpression(left=p[1], operator="IN", right=p[4])
        else:
            logger.debug(f"p_comparison_expression: unexpected len(p)={len(p)}")
            p[0] = None
    else:
        logger.debug(f"p_comparison_expression: unexpected len(p)={len(p)}")
        p[0] = None


def p_primary_expression(p: Any) -> None:
    """primary_expression : column_expression
    | STRING_LITERAL
    | NUMBER_LITERAL
    | BOOLEAN_LITERAL
    | NULL
    | LEFT_PAREN expression RIGHT_PAREN
    | NOT primary_expression
    | primary_expression PLUS primary_expression
    | primary_expression MINUS primary_expression
    | primary_expression ASTERISK primary_expression
    | primary_expression DIVIDE primary_expression"""
    if len(p) == 2:
        logger.debug("p_primary_expression: column_expression or literal")
        # Check the type of p[1] to determine which alternative was matched
        if p[1] == "NULL":
            p[0] = Literal(value=None, type="null")
        elif isinstance(p[1], str) and p[1].startswith("'") and p[1].endswith("'"):
            # STRING_LITERAL
            p[0] = Literal(value=p[1], type="string")
        elif isinstance(p[1], (int, float)):
            # NUMBER_LITERAL
            p[0] = Literal(value=p[1], type="number")
        elif isinstance(p[1], bool):
            # BOOLEAN_LITERAL
            p[0] = Literal(value=p[1], type="boolean")
        elif hasattr(p[1], "__class__") and p[1].__class__.__name__ in [
            "ColumnReference",
            "FunctionCall",
        ]:
            # column_reference or function_call from column_expression
            p[0] = p[1]
        elif hasattr(p[1], "__class__") and p[1].__class__.__name__ == "Literal":
            # propagate Literal from column_expression
            p[0] = p[1]
        elif (
            hasattr(p[1], "__class__") and p[1].__class__.__name__ == "BinaryExpression"
        ):
            # propagate BinaryExpression from column_expression
            p[0] = p[1]
        else:
            # Fallback for other string literals
            p[0] = Literal(value=p[1], type="string")
    elif len(p) == 3:
        if p[1].upper() == "NOT":
            logger.debug("p_primary_expression: NOT primary_expression")
            p[0] = UnaryExpression(operator="NOT", operand=p[2])
        else:
            logger.debug(f"p_primary_expression: unexpected len(p)={len(p)}")
            p[0] = None
    elif len(p) == 4:
        # Check which 4-token expression was matched
        if p[1] == "(":
            logger.debug("p_primary_expression: LEFT_PAREN expression RIGHT_PAREN")
            p[0] = p[2]
        elif p[2] in ("+", "-", "*", "/"):
            logger.debug(
                f"p_primary_expression: primary_expression {p[2]} primary_expression"
            )
            p[0] = BinaryExpression(left=p[1], operator=p[2], right=p[3])
        else:
            logger.debug(f"p_primary_expression: unexpected len(p)={len(p)}")
            p[0] = None
    else:
        logger.debug(f"p_primary_expression: unexpected len(p)={len(p)}")
        p[0] = None


def p_empty(p: Any) -> None:
    """empty :"""
    if len(p) == 1:
        logger.debug("p_empty: valid")
        p[0] = "EMPTY_SENTINEL"  # Special sentinel value to distinguish from None
    else:
        logger.debug(f"p_empty: unexpected len(p)={len(p)}")
        p[0] = None


def p_error(p: Any) -> None:
    """Error rule for syntax errors."""
    if p:
        error_msg = f"Syntax error at '{p.value}' at line {p.lineno}, column {p.lexpos}"
        logger.error(f"{error_msg}")
        raise ParserError(error_msg)
    else:
        error_msg = "Unexpected end of input"
        logger.error(f"{error_msg}")
        raise ParserError(error_msg)


# Build the parser
parser = yacc.yacc()


class PLYParser:
    """PLY-based SQL parser."""

    _parse_tree_run_subfolder = None  # Class variable to persist subfolder for a run

    def __init__(self) -> None:
        logger.info("Initializing parser")
        self.parser = parser
        self.lexer = lexer
        logger.info("Parser initialization complete")

    def parse(self, sql: str) -> Any:
        """Parse SQL query and return AST."""
        logger.info(f"Parsing SQL: {sql[:50]}{'...' if len(sql) > 50 else ''}")
        try:
            result = self.parser.parse(sql, lexer=self.lexer)
            from ..common import config

            if getattr(config, "generate_parse_tree_images", False):
                logger.debug("Generating parse tree image")
                self.generate_parse_tree_image(sql)
            logger.info("SQL parsing completed successfully")
            return result
        except Exception as e:
            logger.error(f"Parsing error: {str(e)}")
            if isinstance(e, ParserError):
                raise
            raise ParserError(f"Parsing error: {str(e)}")

    def reset(self) -> None:
        """Reset parser state."""
        logger.debug("Resetting parser state")
        self.lexer.lineno = 1

    def generate_parse_tree_image(
        self, sql: str, output_path: Optional[str] = None
    ) -> None:
        """Parse SQL and generate a parse tree image using graphviz. If output_path is not provided, use config.PARSE_TREE_IMAGE_DIR and a generated filename in a run-unique subfolder."""
        import os
        import hashlib
        import time
        from typing import Any, Optional
        import textwrap

        logger.info(f"Generating parse tree for SQL: {sql}")
        if output_path is None:
            os.makedirs(config.PARSE_TREE_IMAGE_DIR, exist_ok=True)
            # Use a run-unique subfolder for all images in this run
            if PLYParser._parse_tree_run_subfolder is None:
                run_id = f"run_{int(time.time())}_{uuid.uuid4().hex[:8]}"
                subfolder = os.path.join(config.PARSE_TREE_IMAGE_DIR, run_id)
                os.makedirs(subfolder, exist_ok=True)
                PLYParser._parse_tree_run_subfolder = subfolder
            else:
                subfolder = PLYParser._parse_tree_run_subfolder
        result = self.parser.parse(sql, lexer=self.lexer)
        dot = Digraph(comment="Parse Tree")
        dot.attr(rankdir="LR")  # Make the tree grow sideways (taller, not wider)
        node_id: list[int] = [0]

        # Add the SQL statement as the root node in the graph, pretty-printed and word-wrapped
        sql_label = textwrap.fill(sql.strip(), width=60)
        sql_node_id = "sql_root"
        dot.node(
            sql_node_id,
            f"SQL:\n{sql_label}",
            shape="box",
            style="filled",
            fillcolor="#f0f0f0",
            fontname="monospace",
            fontsize="12",
        )
        node_id[0] = 1  # Start AST nodes from 1 to avoid collision

        def add_node(
            node: Any, parent_id: Optional[str] = None, attr_name: Optional[str] = None
        ) -> None:
            curr_id = str(node_id[0])
            # For leaf nodes, show attribute name and value, and use a different shape
            if isinstance(node, (str, int, float, bool)) or node is None:
                if attr_name is not None:
                    label = f"{attr_name}: {repr(node)}"
                else:
                    label = repr(node)
                dot.node(curr_id, label, shape="note")
            elif isinstance(node, dict):
                if attr_name is not None:
                    label = f"{attr_name}: {str(node)}"
                else:
                    label = str(node)
                dot.node(curr_id, label, shape="note")
            elif hasattr(node, "__class__") and hasattr(node, "__dict__"):
                label = type(node).__name__  # non-leaf AST node
                color = config.PARSE_TREE_NODE_COLORS.get(
                    label, config.PARSE_TREE_DEFAULT_NODE_COLOR
                )
                dot.node(curr_id, label, style="filled", fillcolor=color)
            else:
                label = str(node)
                dot.node(curr_id, label, shape="note")
            if parent_id is not None:
                dot.edge(parent_id, curr_id)
            node_id[0] += 1
            if hasattr(node, "__dict__"):
                for k, v in node.__dict__.items():
                    if isinstance(v, tuple) and k == "limit":
                        # Special handling for (limit, offset)
                        add_node(v[0], curr_id, attr_name="limit")
                        add_node(v[1], curr_id, attr_name="offset")
                    elif isinstance(v, (list, tuple)):
                        for item in v:
                            add_node(item, curr_id, attr_name=k)
                    elif v is not None:
                        add_node(v, curr_id, attr_name=k)
            elif isinstance(node, (list, tuple)):
                for item in node:
                    add_node(item, curr_id)

        # Attach the AST to the SQL root node
        add_node(result, parent_id=sql_node_id)
        # Remove root_type logic, as the SQL root node is now always present
        # Always construct the filename with a hash of the SQL
        if output_path is None:
            sql_hash = hashlib.md5(sql.encode()).hexdigest()
            filename = f"parse_tree_{sql_hash}_{int(time.time())}.png"
            output_path = os.path.join(subfolder, filename)
        dot.render(output_path, format="png", cleanup=True)
        logger.info(f"Parse tree image saved to {output_path}")
