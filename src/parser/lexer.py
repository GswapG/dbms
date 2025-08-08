"""SQL lexer using PLY (Python Lex-Yacc)."""

import ply.lex as lex
from typing import List, Optional, Any
from ..common.errors import ParserError


class TokenType:
    """Token types for SQL lexer."""

    # Keywords
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    INSERT = "INSERT"
    INTO = "INTO"
    VALUES = "VALUES"
    UPDATE = "UPDATE"
    SET = "SET"
    DELETE = "DELETE"
    CREATE = "CREATE"
    TABLE = "TABLE"
    DATABASE = "DATABASE"
    DROP = "DROP"
    ALTER = "ALTER"
    ADD = "ADD"
    COLUMN = "COLUMN"
    PRIMARY = "PRIMARY"
    KEY = "KEY"
    NOT = "NOT"
    NULL = "NULL"
    INTEGER = "INTEGER"
    VARCHAR = "VARCHAR"
    CHAR = "CHAR"
    BOOLEAN = "BOOLEAN"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    DATE = "DATE"
    TIMESTAMP = "TIMESTAMP"
    TEXT = "TEXT"
    BLOB = "BLOB"
    ORDER = "ORDER"
    BY = "BY"
    LIMIT = "LIMIT"
    OFFSET = "OFFSET"
    GROUP = "GROUP"
    HAVING = "HAVING"
    JOIN = "JOIN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    INNER = "INNER"
    OUTER = "OUTER"
    ON = "ON"
    AS = "AS"
    DISTINCT = "DISTINCT"
    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MAX = "MAX"
    MIN = "MIN"
    ASC = "ASC"
    DESC = "DESC"

    # Operators
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    LESS_THAN = "LESS_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_THAN = "GREATER_THAN"
    GREATER_EQUAL = "GREATER_EQUAL"
    AND = "AND"
    OR = "OR"
    LIKE = "LIKE"
    IN = "IN"
    BETWEEN = "BETWEEN"
    IS = "IS"
    PLUS = "PLUS"
    MINUS = "MINUS"
    DIVIDE = "DIVIDE"

    # Punctuation
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    PERIOD = "PERIOD"
    ASTERISK = "ASTERISK"

    # Literals
    IDENTIFIER = "IDENTIFIER"
    STRING_LITERAL = "STRING_LITERAL"
    NUMBER_LITERAL = "NUMBER_LITERAL"
    BOOLEAN_LITERAL = "BOOLEAN_LITERAL"


# List of token names
tokens = (
    "SELECT",
    "FROM",
    "WHERE",
    "INSERT",
    "INTO",
    "VALUES",
    "UPDATE",
    "SET",
    "DELETE",
    "CREATE",
    "TABLE",
    "DATABASE",
    "DROP",
    "ALTER",
    "ADD",
    "COLUMN",
    "PRIMARY",
    "KEY",
    "NOT",
    "NULL",
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
    "ORDER",
    "BY",
    "LIMIT",
    "OFFSET",
    "GROUP",
    "HAVING",
    "JOIN",
    "LEFT",
    "RIGHT",
    "INNER",
    "OUTER",
    "ON",
    "AS",
    "DISTINCT",
    "COUNT",
    "SUM",
    "AVG",
    "MAX",
    "MIN",
    "ASC",
    "DESC",
    "AND",
    "OR",
    "LIKE",
    "IN",
    "BETWEEN",
    "IS",
    "EQUALS",
    "NOT_EQUALS",
    "LESS_THAN",
    "LESS_EQUAL",
    "GREATER_THAN",
    "GREATER_EQUAL",
    "PLUS",
    "MINUS",
    "DIVIDE",
    "COMMA",
    "SEMICOLON",
    "LEFT_PAREN",
    "RIGHT_PAREN",
    "PERIOD",
    "ASTERISK",
    "IDENTIFIER",
    "STRING_LITERAL",
    "NUMBER_LITERAL",
    "BOOLEAN_LITERAL",
)

# Reserved words mapping
reserved = {
    "select": "SELECT",
    "from": "FROM",
    "where": "WHERE",
    "insert": "INSERT",
    "into": "INTO",
    "values": "VALUES",
    "update": "UPDATE",
    "set": "SET",
    "delete": "DELETE",
    "create": "CREATE",
    "table": "TABLE",
    "database": "DATABASE",
    "drop": "DROP",
    "alter": "ALTER",
    "add": "ADD",
    "column": "COLUMN",
    "primary": "PRIMARY",
    "key": "KEY",
    "not": "NOT",
    "null": "NULL",
    "integer": "INTEGER",
    "varchar": "VARCHAR",
    "char": "CHAR",
    "boolean": "BOOLEAN",
    "float": "FLOAT",
    "double": "DOUBLE",
    "date": "DATE",
    "timestamp": "TIMESTAMP",
    "text": "TEXT",
    "blob": "BLOB",
    "order": "ORDER",
    "by": "BY",
    "limit": "LIMIT",
    "offset": "OFFSET",
    "group": "GROUP",
    "having": "HAVING",
    "join": "JOIN",
    "left": "LEFT",
    "right": "RIGHT",
    "inner": "INNER",
    "outer": "OUTER",
    "on": "ON",
    "as": "AS",
    "distinct": "DISTINCT",
    "count": "COUNT",
    "sum": "SUM",
    "avg": "AVG",
    "max": "MAX",
    "min": "MIN",
    "asc": "ASC",
    "desc": "DESC",
    "and": "AND",
    "or": "OR",
    "like": "LIKE",
    "in": "IN",
    "between": "BETWEEN",
    "is": "IS",
    "true": "BOOLEAN_LITERAL",
    "false": "BOOLEAN_LITERAL",
}

# Token definitions
t_EQUALS = r"="
t_NOT_EQUALS = r"!="
t_LESS_EQUAL = r"<="
t_GREATER_EQUAL = r">="
t_LESS_THAN = r"<"
t_GREATER_THAN = r">"
t_PLUS = r"\+"
t_MINUS = r"-"
t_DIVIDE = r"/"
t_COMMA = r","
t_SEMICOLON = r";"
t_LEFT_PAREN = r"\("
t_RIGHT_PAREN = r"\)"
t_PERIOD = r"\."
t_ASTERISK = r"\*"


# String literals
def t_STRING_LITERAL(t: Any) -> Any:
    r"'([^']|'')*'"
    # Remove the outer quotes
    inner = t.value[1:-1]
    # Replace doubled single quotes with a single quote
    t.value = inner.replace("''", "'")
    return t


# Unterminated string literal
def t_UNTERMINATED_STRING(t: Any) -> Any:
    r"'([^']|'')*$"
    raise ParserError("Unterminated string")


# Number literals
def t_NUMBER_LITERAL(t: Any) -> Any:
    r"\d+(?:\.\d+)?"
    t.value = float(t.value) if "." in t.value else int(t.value)
    return t


# Identifiers and reserved words
def t_IDENTIFIER(t: Any) -> Any:
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value.lower(), "IDENTIFIER")
    if t.type == "BOOLEAN_LITERAL":
        t.value = t.value.lower() == "true"
    return t


# Boolean literals
def t_BOOLEAN_LITERAL(t: Any) -> Any:
    r"\b(true|false)\b"
    t.value = t.value.lower() == "true"
    return t


# Ignore whitespace
t_ignore = " \t\n"


# Ignore comments
def t_COMMENT(t: Any) -> None:
    r"--.*"
    pass


# Multiline comments
def t_MULTILINE_COMMENT(t: Any) -> None:
    r"/\*[\s\S]*?\*/"
    pass


# Unterminated multiline comment
def t_UNTERMINATED_COMMENT(t: Any) -> None:
    r"/\*[\s\S]*$"
    raise ParserError("Unterminated comment")


def t_error(t: Any) -> None:
    raise ParserError(
        f"Illegal character '{t.value[0]}' at line {t.lineno}, column {t.lexpos}"
    )


# Build the lexer
lexer = lex.lex()


class SQLLexer:
    """SQL lexer wrapper for PLY lexer."""

    def __init__(self) -> None:
        self.lexer = lexer

    def tokenize(self, sql: str) -> List[lex.LexToken]:
        """Tokenize the SQL query string."""
        self.lexer.input(sql)
        tokens = []

        while True:
            token = self.lexer.token()
            if not token:
                break
            tokens.append(token)

        return tokens

    def reset(self) -> None:
        """Reset the lexer state."""
        self.lexer.lineno = 1
