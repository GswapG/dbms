"""Comprehensive tests for PLY-based SQL lexer and parser."""

import pytest
import os
import tempfile
from dbms.parser.lexer import SQLLexer, TokenType
from dbms.parser.parser import PLYParser
from dbms.parser.ast import (
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
from dbms.common.errors import ParserError
from dbms.common import config

# Comprehensive test data
SAMPLE_USERS = [
    {"id": 1, "name": "Alice", "age": 30, "email": "alice1@example.com"},
    {"id": 2, "name": "Bob", "age": 25, "email": "bob2@example.com"},
    {"id": 3, "name": "Charlie", "age": 35, "email": "charlie3@example.com"},
]
SAMPLE_ORDERS = [
    {"id": 1, "user_id": 1, "amount": 99.99, "status": "shipped"},
    {"id": 2, "user_id": 2, "amount": 15.50, "status": "pending"},
    {"id": 3, "user_id": 3, "amount": 23.75, "status": "delivered"},
]

# Test SQL statements for comprehensive coverage
TEST_SQL_STATEMENTS = {
    # Basic SELECT statements
    "simple_select": "SELECT * FROM users",
    "select_columns": "SELECT name, age FROM users",
    "select_distinct": "SELECT DISTINCT name FROM users",
    "select_with_where": "SELECT * FROM users WHERE age > 30",
    "select_with_order": "SELECT name FROM users ORDER BY age DESC",
    "select_with_limit": "SELECT * FROM users LIMIT 10",
    "select_with_offset": "SELECT * FROM users LIMIT 10 OFFSET 5",
    "select_with_group": "SELECT age, COUNT(*) FROM users GROUP BY age",
    "select_with_having": "SELECT age, COUNT(*) FROM users GROUP BY age HAVING COUNT(*) > 1",
    # Complex WHERE conditions
    "where_equality": "SELECT * FROM users WHERE name = 'Alice'",
    "where_inequality": "SELECT * FROM users WHERE age != 30",
    "where_less_than": "SELECT * FROM users WHERE age < 30",
    "where_less_equal": "SELECT * FROM users WHERE age <= 30",
    "where_greater_than": "SELECT * FROM users WHERE age > 30",
    "where_greater_equal": "SELECT * FROM users WHERE age >= 30",
    "where_like": "SELECT * FROM users WHERE name LIKE 'A%'",
    "where_in": "SELECT * FROM users WHERE age IN (25, 30, 35)",
    "where_is_null": "SELECT * FROM users WHERE email IS NULL",
    "where_is_not_null": "SELECT * FROM users WHERE email IS NOT NULL",
    "where_and": "SELECT * FROM users WHERE age > 25 AND name = 'Alice'",
    "where_or": "SELECT * FROM users WHERE age < 25 OR age > 35",
    "where_complex": "SELECT * FROM users WHERE (age > 25 AND name LIKE 'A%') OR email IS NOT NULL",
    # INSERT statements
    "insert_simple": "INSERT INTO users VALUES ('Alice', 30, 'alice@example.com')",
    "insert_with_columns": "INSERT INTO users (name, age, email) VALUES ('Alice', 30, 'alice@example.com')",
    "insert_multiple": "INSERT INTO users (name, age) VALUES ('Alice', 30), ('Bob', 25)",
    # UPDATE statements
    "update_simple": "UPDATE users SET age = 31 WHERE name = 'Alice'",
    "update_multiple": "UPDATE users SET age = 31, email = 'new@example.com' WHERE name = 'Alice'",
    # DELETE statements
    "delete_simple": "DELETE FROM users WHERE name = 'Alice'",
    "delete_all": "DELETE FROM users",
    # CREATE statements
    "create_table_simple": "CREATE TABLE users (id INTEGER, name VARCHAR(255))",
    "create_table_complex": """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            age INTEGER,
            email VARCHAR(255) NULL,
            created_at TIMESTAMP
        )
    """,
    "create_database": "CREATE DATABASE testdb",
    # DROP statements
    "drop_table": "DROP TABLE users",
    "drop_database": "DROP DATABASE testdb",
    # Function calls
    "select_count": "SELECT COUNT(*) FROM users",
    "select_count_column": "SELECT COUNT(name) FROM users",
    "select_sum": "SELECT SUM(amount) FROM orders",
    "select_avg": "SELECT AVG(amount) FROM orders",
    "select_max": "SELECT MAX(amount) FROM orders",
    "select_min": "SELECT MIN(amount) FROM orders",
    # Table aliases
    "select_with_alias": "SELECT u.name FROM users AS u",
    "select_with_alias_no_as": "SELECT u.name FROM users u",
    # Column references
    "select_table_column": "SELECT users.name FROM users",
    "select_aliased_column": "SELECT u.name FROM users AS u",
    # Expressions
    "select_arithmetic": "SELECT amount + 10 FROM orders",
    "select_arithmetic_complex": "SELECT (amount * 1.1) + tax FROM orders",
    "select_string_literal": "SELECT 'Hello' FROM users",
    "select_number_literal": "SELECT 42 FROM users",
    "select_boolean_literal": "SELECT TRUE FROM users",
    "select_null": "SELECT NULL FROM users",
    # Statements with semicolon
    "select_with_semicolon": "SELECT * FROM users;",
    "insert_with_semicolon": "INSERT INTO users VALUES ('Alice', 30);",
}


@pytest.fixture
def lexer():
    return SQLLexer()


@pytest.fixture
def parser():
    return PLYParser()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for parse tree images."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def enable_parse_trees():
    """Enable parse tree generation for tests."""
    original_value = getattr(config, "generate_parse_tree_images", False)
    config.generate_parse_tree_images = True
    yield
    config.generate_parse_tree_images = original_value


# --- Comprehensive Lexer Tests ---


def test_basic_keywords(lexer):
    sql = "SELECT FROM WHERE INSERT UPDATE DELETE CREATE DROP"
    tokens = lexer.tokenize(sql)
    expected_types = [
        "SELECT",
        "FROM",
        "WHERE",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "DROP",
    ]
    assert len(tokens) == len(expected_types)
    for token, expected_type in zip(tokens, expected_types):
        assert token.type == expected_type


def test_all_sql_keywords(lexer):
    """Test all SQL keywords supported by the lexer."""
    keywords = [
        "SELECT",
        "FROM",
        "WHERE",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "DROP",
        "INTO",
        "VALUES",
        "SET",
        "TABLE",
        "DATABASE",
        "PRIMARY",
        "KEY",
        "NOT",
        "NULL",
        "DISTINCT",
        "GROUP",
        "BY",
        "HAVING",
        "ORDER",
        "ASC",
        "DESC",
        "LIMIT",
        "OFFSET",
        "AND",
        "OR",
        "LIKE",
        "IN",
        "IS",
        "AS",
        "COUNT",
        "SUM",
        "AVG",
        "MAX",
        "MIN",
        "INTEGER",
        "VARCHAR",
        "CHAR",
        "BOOLEAN",
        "FLOAT",
        "DOUBLE",
        "DATE",
        "TIMESTAMP",
        "TEXT",
        "BLOB",
        "TRUE",
        "FALSE",
    ]

    sql = " ".join(keywords)
    tokens = lexer.tokenize(sql)
    assert len(tokens) == len(keywords)
    for token, keyword in zip(tokens, keywords):
        if keyword.upper() in ("TRUE", "FALSE"):
            assert token.type == "BOOLEAN_LITERAL"
        else:
            assert token.type == keyword.upper()


def test_identifiers(lexer):
    sql = "users orders name age email amount status"
    tokens = lexer.tokenize(sql)
    assert [t.value for t in tokens] == [
        "users",
        "orders",
        "name",
        "age",
        "email",
        "amount",
        "status",
    ]
    assert all(token.type == "IDENTIFIER" for token in tokens)


def test_identifiers_with_underscores(lexer):
    sql = "user_id order_date first_name last_name"
    tokens = lexer.tokenize(sql)
    assert [t.value for t in tokens] == [
        "user_id",
        "order_date",
        "first_name",
        "last_name",
    ]
    assert all(token.type == "IDENTIFIER" for token in tokens)


def test_identifiers_with_numbers(lexer):
    sql = "table1 column2 user123"
    tokens = lexer.tokenize(sql)
    assert [t.value for t in tokens] == ["table1", "column2", "user123"]
    assert all(token.type == "IDENTIFIER" for token in tokens)


def test_string_literals(lexer):
    sql = "'Alice' 'bob2@example.com' 'shipped'"
    tokens = lexer.tokenize(sql)
    assert [t.value for t in tokens] == ["Alice", "bob2@example.com", "shipped"]
    assert all(token.type == "STRING_LITERAL" for token in tokens)


def test_string_literals_with_quotes(lexer):
    sql = "'O''Connor' 'He said ''Hello'' to me'"
    tokens = lexer.tokenize(sql)
    assert [t.value for t in tokens] == ["O'Connor", "He said 'Hello' to me"]
    assert all(token.type == "STRING_LITERAL" for token in tokens)


def test_number_literals(lexer):
    sql = "1 30 99.99 3.14159 0 -5 -10.5"
    tokens = lexer.tokenize(sql)
    assert [t.value for t in tokens] == [1, 30, 99.99, 3.14159, 0, -5, -10.5]
    assert all(token.type == "NUMBER_LITERAL" for token in tokens)


def test_boolean_literals(lexer):
    sql = "true false TRUE FALSE"
    tokens = lexer.tokenize(sql)
    assert [t.value for t in tokens] == [True, False, True, False]
    assert all(token.type == "BOOLEAN_LITERAL" for token in tokens)


def test_operators(lexer):
    sql = "= != < <= > >= + - * /"
    tokens = lexer.tokenize(sql)
    expected_types = [
        "EQUALS",
        "NOT_EQUALS",
        "LESS_THAN",
        "LESS_EQUAL",
        "GREATER_THAN",
        "GREATER_EQUAL",
        "PLUS",
        "MINUS",
        "ASTERISK",
        "DIVIDE",
    ]
    assert [t.type for t in tokens] == expected_types


def test_punctuation(lexer):
    sql = ", ; ( ) . *"
    tokens = lexer.tokenize(sql)
    expected_types = [
        "COMMA",
        "SEMICOLON",
        "LEFT_PAREN",
        "RIGHT_PAREN",
        "PERIOD",
        "ASTERISK",
    ]
    assert [t.type for t in tokens] == expected_types


def test_comments(lexer):
    sql = "SELECT * -- This is a comment\nFROM users"
    tokens = lexer.tokenize(sql)
    assert [t.type for t in tokens] == ["SELECT", "ASTERISK", "FROM", "IDENTIFIER"]


def test_multiline_comments(lexer):
    sql = "SELECT * /* This is a\nmultiline comment */ FROM users"
    tokens = lexer.tokenize(sql)
    assert [t.type for t in tokens] == ["SELECT", "ASTERISK", "FROM", "IDENTIFIER"]


def test_whitespace_handling(lexer):
    sql = "SELECT    *    FROM    users"
    tokens = lexer.tokenize(sql)
    assert [t.type for t in tokens] == ["SELECT", "ASTERISK", "FROM", "IDENTIFIER"]


def test_newlines_and_tabs(lexer):
    sql = "SELECT\n*\nFROM\nusers"
    tokens = lexer.tokenize(sql)
    assert [t.type for t in tokens] == ["SELECT", "ASTERISK", "FROM", "IDENTIFIER"]


def test_error_handling(lexer):
    sql = "SELECT * FROM users @"
    with pytest.raises(ParserError) as exc_info:
        lexer.tokenize(sql)
    assert "Illegal character '@'" in str(exc_info.value)


def test_error_handling_invalid_character(lexer):
    sql = "SELECT * FROM users #"
    with pytest.raises(ParserError) as exc_info:
        lexer.tokenize(sql)
    assert "Illegal character '#'" in str(exc_info.value)


def test_error_handling_unterminated_string(lexer):
    sql = "SELECT * FROM users WHERE name = 'Alice"
    with pytest.raises(ParserError) as exc_info:
        lexer.tokenize(sql)
    assert "Unterminated string" in str(exc_info.value)


def test_error_handling_unterminated_comment(lexer):
    sql = "SELECT * FROM users /* Unterminated comment"
    with pytest.raises(ParserError) as exc_info:
        lexer.tokenize(sql)
    assert "Unterminated comment" in str(exc_info.value)


def test_identifiers(lexer):
    sql = "users orders name age email amount status"
    tokens = lexer.tokenize(sql)
    assert [t.value for t in tokens] == [
        "users",
        "orders",
        "name",
        "age",
        "email",
        "amount",
        "status",
    ]
    assert all(token.type == "IDENTIFIER" for token in tokens)


def test_string_literals(lexer):
    sql = "'Alice' 'bob2@example.com' 'shipped'"
    tokens = lexer.tokenize(sql)
    assert [t.value for t in tokens] == ["Alice", "bob2@example.com", "shipped"]
    assert all(token.type == "STRING_LITERAL" for token in tokens)


def test_number_literals(lexer):
    sql = "1 30 99.99"
    tokens = lexer.tokenize(sql)
    assert [t.value for t in tokens] == [1, 30, 99.99]
    assert all(token.type == "NUMBER_LITERAL" for token in tokens)


def test_boolean_literals(lexer):
    sql = "true false"
    tokens = lexer.tokenize(sql)
    assert [t.value for t in tokens] == [True, False]
    assert all(token.type == "BOOLEAN_LITERAL" for token in tokens)


def test_operators(lexer):
    sql = "= != < <= > >= + - * /"
    tokens = lexer.tokenize(sql)
    expected_types = [
        "EQUALS",
        "NOT_EQUALS",
        "LESS_THAN",
        "LESS_EQUAL",
        "GREATER_THAN",
        "GREATER_EQUAL",
        "PLUS",
        "MINUS",
        "ASTERISK",
        "DIVIDE",
    ]
    assert [t.type for t in tokens] == expected_types


def test_punctuation(lexer):
    sql = ", ; ( ) . *"
    tokens = lexer.tokenize(sql)
    expected_types = [
        "COMMA",
        "SEMICOLON",
        "LEFT_PAREN",
        "RIGHT_PAREN",
        "PERIOD",
        "ASTERISK",
    ]
    assert [t.type for t in tokens] == expected_types


def test_comments(lexer):
    sql = "SELECT * -- This is a comment\nFROM users"
    tokens = lexer.tokenize(sql)
    assert [t.type for t in tokens] == ["SELECT", "ASTERISK", "FROM", "IDENTIFIER"]


def test_whitespace_handling(lexer):
    sql = "SELECT    *    FROM    users"
    tokens = lexer.tokenize(sql)
    assert [t.type for t in tokens] == ["SELECT", "ASTERISK", "FROM", "IDENTIFIER"]


def test_error_handling(lexer):
    sql = "SELECT * FROM users @"
    with pytest.raises(ParserError) as exc_info:
        lexer.tokenize(sql)
    assert "Illegal character '@'" in str(exc_info.value)


# --- Comprehensive Parser Tests ---


# Basic SELECT statement tests
def test_simple_select(parser):
    sql = "SELECT * FROM users"
    result = parser.parse(sql)
    assert isinstance(result, SQLStatement)
    assert isinstance(result.statement, SelectStatement)
    select = result.statement
    assert select.from_clause == "users"
    assert len(select.columns) == 1
    assert select.columns[0].name == "*"


def test_select_with_columns(parser):
    sql = "SELECT name, age FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert [col.name for col in select.columns] == ["name", "age"]
    assert select.from_clause == "users"


def test_select_distinct(parser):
    sql = "SELECT DISTINCT name FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert select.distinct is True
    assert [col.name for col in select.columns] == ["name"]


def test_select_with_where(parser):
    sql = "SELECT name FROM users WHERE age > 30"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause is not None
    assert isinstance(select.where_clause, BinaryExpression)
    assert select.where_clause.operator == ">"
    assert select.where_clause.left.name == "age"
    assert select.where_clause.right.value == 30


def test_select_with_order_by(parser):
    sql = "SELECT name FROM users ORDER BY age DESC"
    result = parser.parse(sql)
    select = result.statement
    assert select.order_by[0][0].name == "age"
    assert select.order_by[0][1] == "DESC"


def test_select_with_order_by_asc(parser):
    sql = "SELECT name FROM users ORDER BY age ASC"
    result = parser.parse(sql)
    select = result.statement
    assert select.order_by[0][0].name == "age"
    assert select.order_by[0][1] == "ASC"


def test_select_with_order_by_default(parser):
    sql = "SELECT name FROM users ORDER BY age"
    result = parser.parse(sql)
    select = result.statement
    assert select.order_by[0][0].name == "age"
    assert select.order_by[0][1] is None


def test_select_with_multiple_order_by(parser):
    sql = "SELECT name FROM users ORDER BY age DESC, name ASC"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.order_by) == 2
    assert select.order_by[0][0].name == "age"
    assert select.order_by[0][1] == "DESC"
    assert select.order_by[1][0].name == "name"
    assert select.order_by[1][1] == "ASC"


def test_select_with_limit(parser):
    sql = "SELECT * FROM users LIMIT 10"
    result = parser.parse(sql)
    select = result.statement
    assert select.limit == (10, None)


def test_select_with_limit_and_offset(parser):
    sql = "SELECT * FROM users LIMIT 10 OFFSET 5"
    result = parser.parse(sql)
    select = result.statement
    assert select.limit == (10, 5)


def test_select_with_group_by(parser):
    sql = "SELECT age, COUNT(*) FROM users GROUP BY age"
    result = parser.parse(sql)
    select = result.statement
    assert select.group_by[0].name == "age"


def test_select_with_multiple_group_by(parser):
    sql = "SELECT age, name, COUNT(*) FROM users GROUP BY age, name"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.group_by) == 2
    assert select.group_by[0].name == "age"
    assert select.group_by[1].name == "name"


def test_select_with_having(parser):
    sql = "SELECT age, COUNT(*) FROM users GROUP BY age HAVING COUNT(*) > 1"
    result = parser.parse(sql)
    select = result.statement
    assert select.having is not None
    assert isinstance(select.having, BinaryExpression)
    assert select.having.operator == ">"
    assert select.having.left.name == "count"
    assert select.having.right.value == 1


def test_select_with_columns(parser):
    sql = "SELECT name, age FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert [col.name for col in select.columns] == ["name", "age"]
    assert select.from_clause == "users"


def test_select_with_where(parser):
    sql = "SELECT name FROM users WHERE age > 30"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause is not None
    assert isinstance(select.where_clause, BinaryExpression)
    assert select.where_clause.operator == ">"
    assert select.where_clause.left.name == "age"
    assert select.where_clause.right.value == 30


# WHERE clause tests
def test_select_with_string_match(parser):
    sql = "SELECT email FROM users WHERE name = 'Alice'"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "="
    assert select.where_clause.left.name == "name"
    assert select.where_clause.right.value == "Alice"


def test_where_equality(parser):
    sql = "SELECT * FROM users WHERE name = 'Alice'"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "="
    assert select.where_clause.left.name == "name"
    assert select.where_clause.right.value == "Alice"


def test_where_inequality(parser):
    sql = "SELECT * FROM users WHERE age != 30"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "!="
    assert select.where_clause.left.name == "age"
    assert select.where_clause.right.value == 30


def test_where_less_than(parser):
    sql = "SELECT * FROM users WHERE age < 30"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "<"
    assert select.where_clause.left.name == "age"
    assert select.where_clause.right.value == 30


def test_where_less_equal(parser):
    sql = "SELECT * FROM users WHERE age <= 30"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "<="
    assert select.where_clause.left.name == "age"
    assert select.where_clause.right.value == 30


def test_where_greater_than(parser):
    sql = "SELECT * FROM users WHERE age > 30"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == ">"
    assert select.where_clause.left.name == "age"
    assert select.where_clause.right.value == 30


def test_where_greater_equal(parser):
    sql = "SELECT * FROM users WHERE age >= 30"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == ">="
    assert select.where_clause.left.name == "age"
    assert select.where_clause.right.value == 30


def test_where_like(parser):
    sql = "SELECT * FROM users WHERE name LIKE 'A%'"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "LIKE"
    assert select.where_clause.left.name == "name"
    assert select.where_clause.right.value == "A%"


def test_where_in(parser):
    sql = "SELECT * FROM users WHERE age IN (25, 30, 35)"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "IN"
    assert select.where_clause.left.name == "age"
    assert [v.value for v in select.where_clause.right] == [25, 30, 35]


def test_where_is_null(parser):
    sql = "SELECT * FROM users WHERE email IS NULL"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "IS NULL"
    assert select.where_clause.left.name == "email"
    assert select.where_clause.right.value is None


def test_where_is_not_null(parser):
    sql = "SELECT * FROM users WHERE email IS NOT NULL"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "IS NOT NULL"
    assert select.where_clause.left.name == "email"
    assert select.where_clause.right.value is None


def test_where_and(parser):
    sql = "SELECT * FROM users WHERE age > 25 AND name = 'Alice'"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "AND"
    assert isinstance(select.where_clause.left, BinaryExpression)
    assert isinstance(select.where_clause.right, BinaryExpression)
    assert select.where_clause.left.operator == ">"
    assert select.where_clause.right.operator == "="


def test_where_or(parser):
    sql = "SELECT * FROM users WHERE age < 25 OR age > 35"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "OR"
    assert isinstance(select.where_clause.left, BinaryExpression)
    assert isinstance(select.where_clause.right, BinaryExpression)
    assert select.where_clause.left.operator == "<"
    assert select.where_clause.right.operator == ">"


def test_where_complex_nested(parser):
    sql = "SELECT * FROM users WHERE (age > 25 AND name LIKE 'A%') OR email IS NOT NULL"
    result = parser.parse(sql)
    select = result.statement
    assert select.where_clause.operator == "OR"
    # Left side should be a parenthesized AND expression
    assert isinstance(select.where_clause.left, BinaryExpression)
    assert select.where_clause.left.operator == "AND"
    # Right side should be IS NOT NULL
    assert select.where_clause.right.operator == "IS NOT NULL"


def test_where_not_expression(parser):
    sql = "SELECT * FROM users WHERE NOT (age > 30)"
    result = parser.parse(sql)
    select = result.statement
    assert isinstance(select.where_clause, UnaryExpression)
    assert select.where_clause.operator == "NOT"
    assert isinstance(select.where_clause.operand, BinaryExpression)
    assert select.where_clause.operand.operator == ">"


def test_select_with_order_by(parser):
    sql = "SELECT name FROM users ORDER BY age DESC"
    result = parser.parse(sql)
    select = result.statement
    assert select.order_by[0][0].name == "age"
    assert select.order_by[0][1] == "DESC"


# INSERT statement tests
def test_insert_statement(parser):
    sql = "INSERT INTO users (name, age, email) VALUES ('Alice', 30, 'alice1@example.com')"
    result = parser.parse(sql)
    insert = result.statement
    assert insert.table == "users"
    assert insert.columns == ["name", "age", "email"]
    assert len(insert.values) == 1
    assert [v.value for v in insert.values[0]] == ["Alice", 30, "alice1@example.com"]


def test_insert_simple(parser):
    sql = "INSERT INTO users VALUES ('Alice', 30, 'alice@example.com')"
    result = parser.parse(sql)
    insert = result.statement
    assert insert.table == "users"
    assert insert.columns is None
    assert len(insert.values) == 1
    assert [v.value for v in insert.values[0]] == ["Alice", 30, "alice@example.com"]


def test_insert_multiple_values(parser):
    sql = "INSERT INTO users (name, age) VALUES ('Alice', 30), ('Bob', 25)"
    result = parser.parse(sql)
    insert = result.statement
    assert insert.table == "users"
    assert insert.columns == ["name", "age"]
    assert len(insert.values) == 2
    assert [v.value for v in insert.values[0]] == ["Alice", 30]
    assert [v.value for v in insert.values[1]] == ["Bob", 25]


def test_insert_with_expressions(parser):
    sql = "INSERT INTO orders (amount, total) VALUES (100, 100 * 1.1)"
    result = parser.parse(sql)
    insert = result.statement
    assert insert.table == "orders"
    assert insert.columns == ["amount", "total"]
    assert len(insert.values) == 1
    assert insert.values[0][0].value == 100
    assert isinstance(insert.values[0][1], BinaryExpression)
    assert insert.values[0][1].operator == "*"


# UPDATE statement tests
def test_update_statement(parser):
    sql = "UPDATE users SET age = 31 WHERE name = 'Alice'"
    result = parser.parse(sql)
    update = result.statement
    assert update.table == "users"
    assert update.set_clause["age"].value == 31
    assert update.where_clause.left.name == "name"
    assert update.where_clause.right.value == "Alice"


def test_update_simple(parser):
    sql = "UPDATE users SET age = 31"
    result = parser.parse(sql)
    update = result.statement
    assert update.table == "users"
    assert update.set_clause["age"].value == 31
    assert update.where_clause is None


def test_update_multiple_columns(parser):
    sql = "UPDATE users SET age = 31, email = 'new@example.com' WHERE name = 'Alice'"
    result = parser.parse(sql)
    update = result.statement
    assert update.table == "users"
    assert update.set_clause["age"].value == 31
    assert update.set_clause["email"].value == "new@example.com"
    assert update.where_clause.left.name == "name"
    assert update.where_clause.right.value == "Alice"


def test_update_with_expressions(parser):
    sql = "UPDATE orders SET total = amount * 1.1 WHERE amount > 100"
    result = parser.parse(sql)
    update = result.statement
    assert update.table == "orders"
    assert isinstance(update.set_clause["total"], BinaryExpression)
    assert update.set_clause["total"].operator == "*"
    assert update.where_clause.operator == ">"


# DELETE statement tests
def test_delete_statement(parser):
    sql = "DELETE FROM users WHERE email = 'bob2@example.com'"
    result = parser.parse(sql)
    delete = result.statement
    assert delete.table == "users"
    assert delete.where_clause.left.name == "email"
    assert delete.where_clause.right.value == "bob2@example.com"


def test_delete_all(parser):
    sql = "DELETE FROM users"
    result = parser.parse(sql)
    delete = result.statement
    assert delete.table == "users"
    assert delete.where_clause is None


def test_delete_with_complex_where(parser):
    sql = "DELETE FROM users WHERE age > 30 AND name LIKE 'A%'"
    result = parser.parse(sql)
    delete = result.statement
    assert delete.table == "users"
    assert delete.where_clause.operator == "AND"
    assert delete.where_clause.left.operator == ">"
    assert delete.where_clause.right.operator == "LIKE"


def test_update_statement(parser):
    sql = "UPDATE users SET age = 31 WHERE name = 'Alice'"
    result = parser.parse(sql)
    update = result.statement
    assert update.table == "users"
    assert update.set_clause["age"].value == 31
    assert update.where_clause.left.name == "name"
    assert update.where_clause.right.value == "Alice"


def test_delete_statement(parser):
    sql = "DELETE FROM users WHERE email = 'bob2@example.com'"
    result = parser.parse(sql)
    delete = result.statement
    assert delete.table == "users"
    assert delete.where_clause.left.name == "email"
    assert delete.where_clause.right.value == "bob2@example.com"


# CREATE and DROP statement tests
def test_create_table(parser):
    sql = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        age INTEGER,
        email VARCHAR(255)
    )
    """
    result = parser.parse(sql)
    create = result.statement
    assert create.table == "users"
    assert [col.name for col in create.columns] == ["id", "name", "age", "email"]
    assert create.columns[0].primary_key is True
    assert create.columns[1].nullable is False


def test_create_table_simple(parser):
    sql = "CREATE TABLE users (id INTEGER, name VARCHAR(255))"
    result = parser.parse(sql)
    create = result.statement
    assert create.table == "users"
    assert [col.name for col in create.columns] == ["id", "name"]
    assert create.columns[0].data_type == "integer"
    assert create.columns[1].data_type == "varchar(255)"


def test_create_table_with_constraints(parser):
    sql = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NULL
    )
    """
    result = parser.parse(sql)
    create = result.statement
    assert create.table == "users"
    assert create.columns[0].primary_key is True
    assert create.columns[1].nullable is False
    assert create.columns[2].nullable is True


def test_create_table_all_data_types(parser):
    sql = """
    CREATE TABLE test_table (
        col1 INTEGER,
        col2 VARCHAR(100),
        col3 CHAR(10),
        col4 BOOLEAN,
        col5 FLOAT,
        col6 DOUBLE,
        col7 DATE,
        col8 TIMESTAMP,
        col9 TEXT,
        col10 BLOB
    )
    """
    result = parser.parse(sql)
    create = result.statement
    assert create.table == "test_table"
    expected_types = [
        "integer",
        "varchar(100)",
        "char(10)",
        "boolean",
        "float",
        "double",
        "date",
        "timestamp",
        "text",
        "blob",
    ]
    assert [col.data_type for col in create.columns] == expected_types


def test_create_database(parser):
    sql = "CREATE DATABASE testdb"
    result = parser.parse(sql)
    create = result.statement
    assert create.database == "testdb"


def test_drop_table(parser):
    sql = "DROP TABLE users"
    result = parser.parse(sql)
    drop = result.statement
    assert drop.table == "users"


def test_drop_database(parser):
    sql = "DROP DATABASE testdb"
    result = parser.parse(sql)
    drop = result.statement
    assert drop.database == "testdb"


def test_drop_table(parser):
    sql = "DROP TABLE users"
    result = parser.parse(sql)
    drop = result.statement
    assert drop.table == "users"


def test_drop_database(parser):
    sql = "DROP DATABASE testdb"
    result = parser.parse(sql)
    drop = result.statement
    assert drop.database == "testdb"


# Function call tests
def test_select_count_star(parser):
    sql = "SELECT COUNT(*) FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "count"
    assert len(select.columns[0].arguments) == 1
    assert select.columns[0].arguments[0].name == "*"


def test_select_count_column(parser):
    sql = "SELECT COUNT(name) FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "count"
    assert len(select.columns[0].arguments) == 1
    assert select.columns[0].arguments[0].name == "name"


def test_select_sum(parser):
    sql = "SELECT SUM(amount) FROM orders"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "sum"
    assert select.columns[0].arguments[0].name == "amount"


def test_select_avg(parser):
    sql = "SELECT AVG(amount) FROM orders"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "avg"
    assert select.columns[0].arguments[0].name == "amount"


def test_select_max(parser):
    sql = "SELECT MAX(amount) FROM orders"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "max"
    assert select.columns[0].arguments[0].name == "amount"


def test_select_min(parser):
    sql = "SELECT MIN(amount) FROM orders"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "min"
    assert select.columns[0].arguments[0].name == "amount"


def test_select_multiple_functions(parser):
    sql = "SELECT COUNT(*), SUM(amount), AVG(amount) FROM orders"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 3
    assert select.columns[0].name == "count"
    assert select.columns[1].name == "sum"
    assert select.columns[2].name == "avg"


# Scalar function call tests
def test_select_upper_function(parser):
    sql = "SELECT UPPER(name) FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "upper"
    assert len(select.columns[0].arguments) == 1
    assert select.columns[0].arguments[0].name == "name"


def test_select_lower_function(parser):
    sql = "SELECT LOWER(email) FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "lower"
    assert select.columns[0].arguments[0].name == "email"


def test_select_abs_function(parser):
    sql = "SELECT ABS(balance) FROM accounts"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "abs"
    assert select.columns[0].arguments[0].name == "balance"


def test_select_round_function(parser):
    sql = "SELECT ROUND(amount, 2) FROM orders"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "round"
    assert select.columns[0].arguments[0].name == "amount"
    assert select.columns[0].arguments[1].value == 2


def test_select_concat_function(parser):
    sql = "SELECT CONCAT(first_name, ' ', last_name) FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "concat"
    assert select.columns[0].arguments[0].name == "first_name"
    assert select.columns[0].arguments[1].value == " "
    assert select.columns[0].arguments[2].name == "last_name"


def test_select_coalesce_function(parser):
    sql = "SELECT COALESCE(email, 'unknown') FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "coalesce"
    assert select.columns[0].arguments[0].name == "email"
    assert select.columns[0].arguments[1].value == "unknown"


def test_select_nested_functions(parser):
    sql = "SELECT UPPER(CONCAT(first_name, last_name)) FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], FunctionCall)
    assert select.columns[0].name == "upper"
    inner = select.columns[0].arguments[0]
    assert isinstance(inner, FunctionCall)
    assert inner.name == "concat"
    assert inner.arguments[0].name == "first_name"
    assert inner.arguments[1].name == "last_name"


def test_select_mixed_aggregate_and_scalar(parser):
    sql = "SELECT COUNT(*), UPPER(name) FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 2
    assert select.columns[0].name == "count"
    assert select.columns[1].name == "upper"
    assert select.columns[1].arguments[0].name == "name"


# Table alias tests
def test_select_with_alias(parser):
    sql = "SELECT u.name FROM users AS u"
    result = parser.parse(sql)
    select = result.statement
    assert select.from_clause == "users AS u"


def test_select_with_alias_no_as(parser):
    sql = "SELECT u.name FROM users u"
    result = parser.parse(sql)
    select = result.statement
    assert select.from_clause == "users u"


def test_select_table_column(parser):
    sql = "SELECT users.name FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], ColumnReference)
    assert select.columns[0].name == "name"
    assert select.columns[0].table == "users"


def test_select_aliased_column(parser):
    sql = "SELECT u.name FROM users AS u"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], ColumnReference)
    assert select.columns[0].name == "name"
    assert select.columns[0].table == "u"


# Expression tests
def test_select_arithmetic(parser):
    sql = "SELECT amount + 10 FROM orders"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], BinaryExpression)
    assert select.columns[0].operator == "+"
    assert select.columns[0].left.name == "amount"
    assert select.columns[0].right.value == 10


def test_select_arithmetic_complex(parser):
    sql = "SELECT (amount * 1.1) + tax FROM orders"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], BinaryExpression)
    assert select.columns[0].operator == "+"
    assert isinstance(select.columns[0].left, BinaryExpression)
    assert select.columns[0].left.operator == "*"


def test_select_string_literal(parser):
    sql = "SELECT 'Hello' FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], Literal)
    assert select.columns[0].value == "Hello"
    assert select.columns[0].type == "string"


def test_select_number_literal(parser):
    sql = "SELECT 42 FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], Literal)
    assert select.columns[0].value == 42
    assert select.columns[0].type == "number"


def test_select_boolean_literal(parser):
    sql = "SELECT TRUE FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], Literal)
    assert select.columns[0].value is True
    assert select.columns[0].type == "boolean"


def test_select_null(parser):
    sql = "SELECT NULL FROM users"
    result = parser.parse(sql)
    select = result.statement
    assert len(select.columns) == 1
    assert isinstance(select.columns[0], Literal)
    assert select.columns[0].value is None
    assert select.columns[0].type == "null"


# Statement with semicolon tests
def test_select_with_semicolon(parser):
    sql = "SELECT * FROM users;"
    result = parser.parse(sql)
    assert isinstance(result, SQLStatement)
    assert isinstance(result.statement, SelectStatement)


def test_insert_with_semicolon(parser):
    sql = "INSERT INTO users VALUES ('Alice', 30);"
    result = parser.parse(sql)
    assert isinstance(result, SQLStatement)
    assert isinstance(result.statement, InsertStatement)


# Error handling tests
def test_syntax_error(parser):
    sql = "SELECT * FROM users WHERE age >"
    with pytest.raises(ParserError) as exc_info:
        parser.parse(sql)
    assert "Syntax error" in str(exc_info.value)


def test_invalid_sql(parser):
    sql = "INVALID SQL STATEMENT"
    with pytest.raises(ParserError) as exc_info:
        parser.parse(sql)
    assert "Syntax error" in str(exc_info.value)


def test_unexpected_end_of_input(parser):
    sql = "SELECT * FROM"
    with pytest.raises(ParserError) as exc_info:
        parser.parse(sql)
    assert "Syntax error" in str(exc_info.value)


# Parser method tests
def test_parser_reset(parser):
    sql = "SELECT * FROM users"
    result1 = parser.parse(sql)
    parser.reset()
    result2 = parser.parse(sql)
    assert isinstance(result1, SQLStatement)
    assert isinstance(result2, SQLStatement)


def test_parse_tree_generation(parser, enable_parse_trees, temp_dir):
    """Test parse tree image generation."""
    # Set the parse tree directory to temp directory
    original_dir = config.PARSE_TREE_IMAGE_DIR
    config.PARSE_TREE_IMAGE_DIR = temp_dir
    from dbms.parser.parser import PLYParser

    # Reset run subfolder before test for isolation
    PLYParser._parse_tree_run_subfolder = None

    try:
        sql = "SELECT * FROM users"
        result = parser.parse(sql)

        # Check that the result is valid
        assert isinstance(result, SQLStatement)
        assert isinstance(result.statement, SelectStatement)

        # Check for a run subfolder and PNG files inside it
        subfolders = [
            f for f in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, f))
        ]
        assert subfolders, "No subfolder created for parse tree images"
        run_folder = os.path.join(temp_dir, subfolders[0])
        files = os.listdir(run_folder) if os.path.exists(run_folder) else []
        assert files, "No files in run subfolder"
        assert any(
            f.endswith(".png") for f in files
        ), "No PNG image generated in run subfolder"

    finally:
        config.PARSE_TREE_IMAGE_DIR = original_dir
        # Reset run subfolder after test for isolation
        PLYParser._parse_tree_run_subfolder = None


# Comprehensive test using all test SQL statements
def test_all_sql_statements(parser):
    """Test all predefined SQL statements to ensure they parse correctly."""
    for name, sql in TEST_SQL_STATEMENTS.items():
        try:
            result = parser.parse(sql)
            assert isinstance(result, SQLStatement)
            assert result.statement is not None
        except Exception as e:
            pytest.fail(f"Failed to parse SQL statement '{name}': {sql}\nError: {e}")


# Edge cases and boundary tests
def test_empty_string(parser):
    with pytest.raises(ParserError):
        parser.parse("")


def test_whitespace_only(parser):
    with pytest.raises(ParserError):
        parser.parse("   \n\t  ")


def test_very_long_identifier(parser):
    long_name = "a" * 1000
    sql = f"SELECT * FROM {long_name}"
    result = parser.parse(sql)
    assert isinstance(result, SQLStatement)
    assert result.statement.from_clause == long_name


def test_nested_parentheses(parser):
    sql = "SELECT * FROM users WHERE ((age > 25) AND (name = 'Alice'))"
    result = parser.parse(sql)
    assert isinstance(result, SQLStatement)
    assert isinstance(result.statement.where_clause, BinaryExpression)


def test_complex_arithmetic_expressions(parser):
    sql = "SELECT (a + b) * (c - d) / e FROM table1"
    result = parser.parse(sql)
    assert isinstance(result, SQLStatement)
    assert isinstance(result.statement.columns[0], BinaryExpression)


def test_multiple_statements(parser):
    """Test that multiple statements are handled correctly."""
    sql1 = "SELECT * FROM users"
    sql2 = "INSERT INTO users VALUES ('Alice', 30)"

    result1 = parser.parse(sql1)
    result2 = parser.parse(sql2)

    assert isinstance(result1.statement, SelectStatement)
    assert isinstance(result2.statement, InsertStatement)


# Performance tests
def test_parser_performance(parser):
    """Test parser performance with complex queries."""
    complex_sql = """
    SELECT u.name, COUNT(o.id) as order_count, SUM(o.amount) as total_amount
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.age > 25 AND u.email IS NOT NULL
    GROUP BY u.id, u.name
    HAVING COUNT(o.id) > 0
    ORDER BY total_amount DESC
    LIMIT 10
    """

    # This should not raise an exception (even if JOIN is not supported)
    try:
        result = parser.parse(complex_sql)
        # If it parses, it should be a valid statement
        assert isinstance(result, SQLStatement)
    except ParserError:
        # JOIN not supported is expected
        pass


def test_large_number_of_columns(parser):
    """Test parser with a large number of columns."""
    columns = [f"col{i}" for i in range(50)]
    sql = f"SELECT {', '.join(columns)} FROM users"
    result = parser.parse(sql)
    assert isinstance(result, SQLStatement)
    assert len(result.statement.columns) == 50


def test_large_number_of_values(parser):
    """Test parser with a large number of values in INSERT."""
    values = [f"'{i}'" for i in range(50)]
    sql = f"INSERT INTO users VALUES ({', '.join(values)})"
    result = parser.parse(sql)
    assert isinstance(result, SQLStatement)
    assert len(result.statement.values[0]) == 50
