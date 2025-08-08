# SQL Parser API Reference

---

## Overview

The SQL parser module provides PLY-based lexer and parser implementations for SQL queries. It supports a comprehensive subset of SQL syntax and generates Abstract Syntax Trees (AST) for further processing.

For implementation details and conceptual information, see [SQL Parser Deep Dive](../explanation/parser.md).

---

## Main Classes

### SQLLexer
The lexer for tokenizing SQL queries using PLY.

```python
class SQLLexer:
    def __init__(self) -> None
    def tokenize(self, sql: str) -> List[lex.LexToken]
    def reset(self) -> None
```

#### Methods

```python
def tokenize(sql: str) -> List[lex.LexToken]
```
- **sql**: SQL query string
- **Returns**: List of PLY lexer tokens
- **Raises**: ParserError on lexical errors (invalid characters, unterminated strings/comments)

```python
def reset() -> None
```
- Resets the lexer state (line numbers, etc.)

#### Token Types

The lexer recognizes the following token types:

**Keywords:**
- `SELECT`, `FROM`, `WHERE`, `INSERT`, `UPDATE`, `DELETE`
- `CREATE`, `DROP`, `TABLE`, `DATABASE`
- `DISTINCT`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`, `OFFSET`
- `AND`, `OR`, `NOT`, `LIKE`, `IN`, `IS`, `NULL`
- `PRIMARY`, `KEY`, `NOT NULL`, `ASC`, `DESC`
- `COUNT`, `SUM`, `AVG`, `MAX`, `MIN`
- `INTEGER`, `VARCHAR`, `CHAR`, `BOOLEAN`, `FLOAT`, `DOUBLE`, `DATE`, `TIMESTAMP`, `TEXT`, `BLOB`
- `TRUE`, `FALSE`

**Operators:**
- `=`, `!=`, `<`, `<=`, `>`, `>=` (comparison)
- `+`, `-`, `*`, `/` (arithmetic)
- `AND`, `OR`, `NOT` (logical)

**Punctuation:**
- `,`, `;`, `(`, `)`, `.`, `*`

**Literals:**
- `IDENTIFIER`: Table names, column names, aliases
- `STRING_LITERAL`: Quoted strings
- `NUMBER_LITERAL`: Integers and floating-point numbers
- `BOOLEAN_LITERAL`: TRUE/FALSE values

---

### PLYParser
The parser for converting SQL tokens into AST nodes.

```python
class PLYParser:
    def __init__(self) -> None
    def parse(self, sql: str) -> SQLStatement
    def reset(self) -> None
    def generate_parse_tree_image(self, sql: str, output_path: Optional[str] = None) -> None
```

#### Methods

```python
def parse(sql: str) -> SQLStatement
```
- **sql**: SQL query string
- **Returns**: Root AST node (SQLStatement)
- **Raises**: ParserError on syntax errors

```python
def reset() -> None
```
- Resets the parser state (lexer line numbers, etc.)

```python
def generate_parse_tree_image(sql: str, output_path: Optional[str] = None) -> None
```
- **sql**: SQL query to visualize
- **output_path**: Optional custom path for the generated image
- **Description**: Generates a visual parse tree using Graphviz

---

## AST Node Types

The parser generates a rich AST with the following node types:

### Statement Nodes
- `SQLStatement`: Root wrapper for all SQL statements
- `SelectStatement`: SELECT queries with all clauses
- `InsertStatement`: INSERT operations
- `UpdateStatement`: UPDATE operations
- `DeleteStatement`: DELETE operations
- `CreateTableStatement`: CREATE TABLE operations
- `CreateDatabaseStatement`: CREATE DATABASE operations
- `DropTableStatement`: DROP TABLE operations
- `DropDatabaseStatement`: DROP DATABASE operations

### Expression Nodes
- `BinaryExpression`: Binary operations (+, -, *, /, =, !=, <, >, etc.)
- `UnaryExpression`: Unary operations (NOT)
- `ColumnReference`: Column references (with optional table qualification)
- `Literal`: Literal values (strings, numbers, booleans, NULL)
- `FunctionCall`: Function calls (COUNT, SUM, AVG, etc.)

### Definition Nodes
- `ColumnDefinition`: Column definitions in CREATE TABLE

---

## Supported SQL Features

The parser supports the following SQL statements:

- **SELECT**: With WHERE, GROUP BY, HAVING, ORDER BY, LIMIT/OFFSET
- **INSERT**: Single and multiple value sets
- **UPDATE**: Multi-column updates with expressions
- **DELETE**: With optional WHERE clauses
- **CREATE TABLE**: With data types and constraints
- **CREATE/DROP DATABASE**: Database management
- **DROP TABLE**: Table removal

For detailed SQL syntax examples, see [SQL Parser Deep Dive](../explanation/parser.md).

---

## Error Handling

- All syntax errors raise `ParserError` with a descriptive message.
- Errors include line number and column position information.

---

## Example Usage

```python
from dbms.parser.parser import PLYParser

parser = PLYParser()

# Simple SELECT
sql = "SELECT id, name FROM users WHERE age > 18"
ast = parser.parse(sql)

# Complex query
sql = """
SELECT DISTINCT u.name, COUNT(o.id) as order_count
FROM users u
WHERE u.age > 18 AND u.status = 'active'
GROUP BY u.name
HAVING COUNT(o.id) > 5
ORDER BY order_count DESC
LIMIT 10
"""
ast = parser.parse(sql)
```

---

## Parse Tree Image Generation

The parser can generate a visual parse tree for any SQL statement using the `graphviz` library.

### Configuration

Enable parse tree generation in `src/common/config.py`:

```python
generate_parse_tree_images = True
PARSE_TREE_IMAGE_DIR = 'parse_trees'
```

### Usage Example

```python
from dbms.parser.parser import PLYParser
from dbms.common import config

# Enable parse tree generation
config.generate_parse_tree_images = True

parser = PLYParser()
sql = "SELECT name, age FROM users WHERE age > 30"
ast = parser.parse(sql)  # Automatically generates parse tree image
```

---

## Grammar Reference

For complete SQL grammar specification, see [Grammar Reference](../explanation/grammar.md).

---

## Implementation Details

For detailed implementation information, see [SQL Parser Deep Dive](../explanation/parser.md).

---

## Related Documentation

- **[SQL Parser Deep Dive](../explanation/parser.md)**: Implementation details and concepts
- **[Grammar Reference](../explanation/grammar.md)**: Complete SQL grammar specification
- **[PLY Documentation](https://www.dabeaz.com/ply/)**: Official PLY documentation
- **[Graphviz Documentation](https://graphviz.org/documentation/)**: Parse tree visualization
