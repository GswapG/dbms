# Supported SQL Features

This document provides a comprehensive overview of the SQL features supported by the PLY-based parser, including syntax examples and the corresponding Abstract Syntax Tree (AST) representations.

## Overview

The SQL parser supports a substantial subset of SQL-92 and SQL-99 standards, focusing on the most commonly used features for database operations. The parser generates structured AST nodes that can be used for query optimization, execution planning, and analysis.

## Data Manipulation Language (DML)

### SELECT Statement

The SELECT statement is the most complex and feature-rich statement supported by the parser.

#### Basic SELECT

**Syntax:**
```sql
SELECT column_list FROM table_reference
```

**Examples:**
```sql
-- Select all columns
SELECT * FROM users

-- Select specific columns
SELECT id, name, email FROM users

-- Select with table alias
SELECT u.name, u.email FROM users AS u
```

**AST Representation:**
```python
SelectStatement(
    columns=[ColumnReference(name="id"), ColumnReference(name="name")],
    from_clause="users",
    where_clause=None,
    distinct=False,
    group_by=None,
    having=None,
    order_by=None,
    limit=None
)
```

#### SELECT with WHERE Clause

**Syntax:**
```sql
SELECT column_list FROM table_reference WHERE expression
```

**Examples:**
```sql
-- Simple condition
SELECT * FROM users WHERE age > 18

-- Multiple conditions with AND
SELECT * FROM users WHERE age > 18 AND status = 'active'

-- Complex conditions with parentheses
SELECT * FROM users WHERE (age > 18 AND status = 'active') OR (age = 0 AND status = 'pending')
```

**AST Representation:**
```python
SelectStatement(
    columns=[ColumnReference(name="*")],
    from_clause="users",
    where_clause=BinaryExpression(
        left=BinaryExpression(
            left=ColumnReference(name="age"),
            operator="GREATER_THAN",
            right=Literal(value=18, type="number")
        ),
        operator="AND",
        right=BinaryExpression(
            left=ColumnReference(name="status"),
            operator="EQUALS",
            right=Literal(value="active", type="string")
        )
    )
)
```

#### SELECT DISTINCT

**Syntax:**
```sql
SELECT DISTINCT column_list FROM table_reference
```

**Example:**
```sql
SELECT DISTINCT department FROM employees
```

**AST Representation:**
```python
SelectStatement(
    columns=[ColumnReference(name="department")],
    from_clause="employees",
    distinct=True
)
```

#### Aggregate Functions

**Supported Functions:**
- `COUNT(*)` - Count all rows
- `COUNT(column)` - Count non-null values in column
- `SUM(column)` - Sum of column values
- `AVG(column)` - Average of column values
- `MAX(column)` - Maximum value in column
- `MIN(column)` - Minimum value in column

**Examples:**
```sql
-- Count all users
SELECT COUNT(*) FROM users

-- Count active users
SELECT COUNT(*) FROM users WHERE status = 'active'

-- Multiple aggregates
SELECT COUNT(*), AVG(age), MAX(salary) FROM employees
```

**AST Representation:**
```python
SelectStatement(
    columns=[
        FunctionCall(name="count", arguments=[ColumnReference(name="*")]),
        FunctionCall(name="avg", arguments=[ColumnReference(name="age")]),
        FunctionCall(name="max", arguments=[ColumnReference(name="salary")])
    ],
    from_clause="employees"
)
```

#### GROUP BY Clause

**Syntax:**
```sql
SELECT column_list FROM table_reference GROUP BY column_list
```

**Examples:**
```sql
-- Group by single column
SELECT department, COUNT(*) FROM employees GROUP BY department

-- Group by multiple columns
SELECT department, role, COUNT(*) FROM employees GROUP BY department, role
```

**AST Representation:**
```python
SelectStatement(
    columns=[
        ColumnReference(name="department"),
        FunctionCall(name="count", arguments=[ColumnReference(name="*")])
    ],
    from_clause="employees",
    group_by=[ColumnReference(name="department")]
)
```

#### HAVING Clause

**Syntax:**
```sql
SELECT column_list FROM table_reference GROUP BY column_list HAVING expression
```

**Example:**
```sql
SELECT department, COUNT(*) as emp_count
FROM employees
GROUP BY department
HAVING COUNT(*) > 5
```

**AST Representation:**
```python
SelectStatement(
    columns=[
        ColumnReference(name="department"),
        FunctionCall(name="count", arguments=[ColumnReference(name="*")])
    ],
    from_clause="employees",
    group_by=[ColumnReference(name="department")],
    having=BinaryExpression(
        left=FunctionCall(name="count", arguments=[ColumnReference(name="*")]),
        operator="GREATER_THAN",
        right=Literal(value=5, type="number")
    )
)
```

#### ORDER BY Clause

**Syntax:**
```sql
SELECT column_list FROM table_reference ORDER BY order_list
```

**Examples:**
```sql
-- Single column ordering
SELECT * FROM users ORDER BY name

-- Multiple column ordering
SELECT * FROM users ORDER BY age DESC, name ASC

-- Order by expression
SELECT name, salary * 1.1 as new_salary FROM employees ORDER BY new_salary DESC
```

**AST Representation:**
```python
SelectStatement(
    columns=[ColumnReference(name="*")],
    from_clause="users",
    order_by=[
        (ColumnReference(name="age"), "DESC"),
        (ColumnReference(name="name"), "ASC")
    ]
)
```

#### LIMIT and OFFSET

**Syntax:**
```sql
SELECT column_list FROM table_reference LIMIT number [OFFSET number]
```

**Examples:**
```sql
-- Limit results
SELECT * FROM users LIMIT 10

-- Limit with offset (pagination)
SELECT * FROM users LIMIT 10 OFFSET 20

-- Alternative syntax (not supported)
-- SELECT * FROM users LIMIT 20, 10
```

**AST Representation:**
```python
SelectStatement(
    columns=[ColumnReference(name="*")],
    from_clause="users",
    limit=(10, 20)  # (limit, offset)
)
```

### INSERT Statement

#### Basic INSERT

**Syntax:**
```sql
INSERT INTO table_name [(column_list)] VALUES (value_list) [, (value_list)...]
```

**Examples:**
```sql
-- Insert single row
INSERT INTO users (name, email, age) VALUES ('John', 'john@example.com', 25)

-- Insert without column specification
INSERT INTO users VALUES ('John', 'john@example.com', 25)

-- Insert multiple rows
INSERT INTO users (name, age) VALUES ('John', 25), ('Jane', 30), ('Bob', 35)
```

**AST Representation:**
```python
InsertStatement(
    table="users",
    columns=["name", "email", "age"],
    values=[[
        Literal(value="John", type="string"),
        Literal(value="john@example.com", type="string"),
        Literal(value=25, type="number")
    ]]
)
```

### UPDATE Statement

#### Basic UPDATE

**Syntax:**
```sql
UPDATE table_name SET column = expression [, column = expression...] [WHERE expression]
```

**Examples:**
```sql
-- Update single column
UPDATE users SET age = 26 WHERE id = 1

-- Update multiple columns
UPDATE users SET name = 'John Doe', email = 'john.doe@example.com' WHERE id = 1

-- Update with expression
UPDATE employees SET salary = salary * 1.1 WHERE department = 'Engineering'
```

**AST Representation:**
```python
UpdateStatement(
    table="users",
    set_clause={
        "name": Literal(value="John Doe", type="string"),
        "email": Literal(value="john.doe@example.com", type="string")
    },
    where_clause=BinaryExpression(
        left=ColumnReference(name="id"),
        operator="EQUALS",
        right=Literal(value=1, type="number")
    )
)
```

### DELETE Statement

#### Basic DELETE

**Syntax:**
```sql
DELETE FROM table_name [WHERE expression]
```

**Examples:**
```sql
-- Delete all rows
DELETE FROM users

-- Delete with condition
DELETE FROM users WHERE age < 18

-- Delete with complex condition
DELETE FROM users WHERE status = 'inactive' AND last_login < '2023-01-01'
```

**AST Representation:**
```python
DeleteStatement(
    table="users",
    where_clause=BinaryExpression(
        left=ColumnReference(name="age"),
        operator="LESS_THAN",
        right=Literal(value=18, type="number")
    )
)
```

## Data Definition Language (DDL)

### CREATE TABLE Statement

#### Basic CREATE TABLE

**Syntax:**
```sql
CREATE TABLE table_name (column_definition [, column_definition...])
```

**Examples:**
```sql
-- Simple table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    age INTEGER
)

-- Complex table with various data types
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    salary FLOAT,
    hire_date DATE,
    is_active BOOLEAN DEFAULT true,
    bio TEXT
)
```

**AST Representation:**
```python
CreateTableStatement(
    table="users",
    columns=[
        ColumnDefinition(
            name="id",
            data_type="integer",
            nullable=True,
            primary_key=True
        ),
        ColumnDefinition(
            name="name",
            data_type="varchar(255)",
            nullable=False
        ),
        ColumnDefinition(
            name="email",
            data_type="varchar(255)",
            nullable=True
        ),
        ColumnDefinition(
            name="age",
            data_type="integer",
            nullable=True
        )
    ]
)
```

#### Supported Data Types

- **INTEGER** - 32-bit integer
- **VARCHAR(n)** - Variable-length string with maximum length n
- **CHAR(n)** - Fixed-length string of length n
- **BOOLEAN** - True/false value
- **FLOAT** - Single-precision floating point
- **DOUBLE** - Double-precision floating point
- **DATE** - Date value
- **TIMESTAMP** - Date and time value
- **TEXT** - Variable-length text
- **BLOB** - Binary large object

#### Supported Constraints

- **PRIMARY KEY** - Primary key constraint
- **NOT NULL** - Column cannot contain NULL values
- **NULL** - Column can contain NULL values (default)

### CREATE DATABASE Statement

**Syntax:**
```sql
CREATE DATABASE database_name
```

**Example:**
```sql
CREATE DATABASE myapp
```

**AST Representation:**
```python
CreateDatabaseStatement(database="myapp")
```

### DROP TABLE Statement

**Syntax:**
```sql
DROP TABLE table_name
```

**Example:**
```sql
DROP TABLE users
```

**AST Representation:**
```python
DropTableStatement(table="users")
```

### DROP DATABASE Statement

**Syntax:**
```sql
DROP DATABASE database_name
```

**Example:**
```sql
DROP DATABASE myapp
```

**AST Representation:**
```python
DropDatabaseStatement(database="myapp")
```

## Expressions

### Comparison Operators

**Supported Operators:**
- `=` - Equal
- `!=` - Not equal
- `<` - Less than
- `<=` - Less than or equal
- `>` - Greater than
- `>=` - Greater than or equal

**Examples:**
```sql
-- Simple comparisons
SELECT * FROM users WHERE age = 25
SELECT * FROM users WHERE age != 25
SELECT * FROM users WHERE age > 18
SELECT * FROM users WHERE age <= 65
```

**AST Representation:**
```python
BinaryExpression(
    left=ColumnReference(name="age"),
    operator="GREATER_THAN",
    right=Literal(value=18, type="number")
)
```

### Logical Operators

**Supported Operators:**
- `AND` - Logical AND
- `OR` - Logical OR
- `NOT` - Logical NOT

**Examples:**
```sql
-- AND operator
SELECT * FROM users WHERE age > 18 AND status = 'active'

-- OR operator
SELECT * FROM users WHERE status = 'active' OR status = 'pending'

-- NOT operator
SELECT * FROM users WHERE NOT (age < 18)

-- Complex logical expressions
SELECT * FROM users WHERE (age > 18 AND status = 'active') OR (age = 0 AND status = 'pending')
```

**AST Representation:**
```python
BinaryExpression(
    left=BinaryExpression(
        left=ColumnReference(name="age"),
        operator="GREATER_THAN",
        right=Literal(value=18, type="number")
    ),
    operator="AND",
    right=BinaryExpression(
        left=ColumnReference(name="status"),
        operator="EQUALS",
        right=Literal(value="active", type="string")
    )
)
```

### Pattern Matching

**LIKE Operator:**
```sql
-- Pattern matching
SELECT * FROM users WHERE name LIKE '%john%'
SELECT * FROM users WHERE email LIKE 'john%@example.com'
SELECT * FROM users WHERE name LIKE 'J_n%'
```

**AST Representation:**
```python
BinaryExpression(
    left=ColumnReference(name="name"),
    operator="LIKE",
    right=Literal(value="%john%", type="string")
)
```

### Set Membership

**IN Operator:**
```sql
-- Set membership
SELECT * FROM users WHERE status IN ('active', 'pending', 'inactive')
SELECT * FROM users WHERE age IN (18, 21, 25, 30)
```

**AST Representation:**
```python
BinaryExpression(
    left=ColumnReference(name="status"),
    operator="IN",
    right=[
        Literal(value="active", type="string"),
        Literal(value="pending", type="string"),
        Literal(value="inactive", type="string")
    ]
)
```

### Null Checking

**IS NULL and IS NOT NULL:**
```sql
-- Null checking
SELECT * FROM users WHERE email IS NULL
SELECT * FROM users WHERE email IS NOT NULL
```

**AST Representation:**
```python
BinaryExpression(
    left=ColumnReference(name="email"),
    operator="IS NULL",
    right=Literal(value=None, type="null")
)
```

### Arithmetic Operators

**Supported Operators:**
- `+` - Addition
- `-` - Subtraction
- `*` - Multiplication
- `/` - Division

**Examples:**
```sql
-- Arithmetic expressions
SELECT id, salary * 1.1 as new_salary FROM employees
SELECT id, (salary + bonus) * 0.9 as net_pay FROM employees
SELECT id, age + 1 as next_year_age FROM users
```

**AST Representation:**
```python
BinaryExpression(
    left=ColumnReference(name="salary"),
    operator="MULTIPLY",
    right=Literal(value=1.1, type="number")
)
```

## Data Types and Literals

### String Literals

**Syntax:**
```sql
'text content'
```

**Examples:**
```sql
SELECT * FROM users WHERE name = 'John Doe'
INSERT INTO users (name) VALUES ('Jane Smith')
```

**AST Representation:**
```python
Literal(value="John Doe", type="string")
```

### Number Literals

**Syntax:**
```sql
123        -- Integer
456.789    -- Float
```

**Examples:**
```sql
SELECT * FROM users WHERE age = 25
UPDATE users SET salary = 50000.50 WHERE id = 1
```

**AST Representation:**
```python
Literal(value=25, type="number")
Literal(value=50000.50, type="number")
```

### Boolean Literals

**Syntax:**
```sql
true
false
```

**Examples:**
```sql
SELECT * FROM users WHERE is_active = true
UPDATE users SET verified = false WHERE email IS NULL
```

**AST Representation:**
```python
Literal(value=True, type="boolean")
Literal(value=False, type="boolean")
```

### Null Literal

**Syntax:**
```sql
NULL
```

**Examples:**
```sql
SELECT * FROM users WHERE email IS NULL
UPDATE users SET last_login = NULL WHERE status = 'inactive'
```

**AST Representation:**
```python
Literal(value=None, type="null")
```

## Complex Query Examples

### Example 1: User Analytics Query

**SQL:**
```sql
SELECT
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    MAX(salary) as max_salary
FROM employees
WHERE hire_date >= '2020-01-01'
    AND status = 'active'
GROUP BY department
HAVING COUNT(*) > 5
ORDER BY avg_salary DESC
LIMIT 10
```

**AST Representation:**
```python
SelectStatement(
    columns=[
        ColumnReference(name="department"),
        FunctionCall(name="count", arguments=[ColumnReference(name="*")]),
        FunctionCall(name="avg", arguments=[ColumnReference(name="salary")]),
        FunctionCall(name="max", arguments=[ColumnReference(name="salary")])
    ],
    from_clause="employees",
    where_clause=BinaryExpression(
        left=BinaryExpression(
            left=ColumnReference(name="hire_date"),
            operator="GREATER_EQUAL",
            right=Literal(value="2020-01-01", type="string")
        ),
        operator="AND",
        right=BinaryExpression(
            left=ColumnReference(name="status"),
            operator="EQUALS",
            right=Literal(value="active", type="string")
        )
    ),
    group_by=[ColumnReference(name="department")],
    having=BinaryExpression(
        left=FunctionCall(name="count", arguments=[ColumnReference(name="*")]),
        operator="GREATER_THAN",
        right=Literal(value=5, type="number")
    ),
    order_by=[(FunctionCall(name="avg", arguments=[ColumnReference(name="salary")]), "DESC")],
    limit=(10, None)
)
```

### Example 2: Data Migration Query

**SQL:**
```sql
INSERT INTO new_users (id, name, email, age, status)
SELECT
    u.id,
    u.name,
    u.email,
    u.age,
    CASE
        WHEN u.last_login > '2023-01-01' THEN 'active'
        ELSE 'inactive'
    END as status
FROM old_users u
WHERE u.email IS NOT NULL
    AND u.name IS NOT NULL
```

**AST Representation:**
```python
InsertStatement(
    table="new_users",
    columns=["id", "name", "email", "age", "status"],
    values=[[
        ColumnReference(name="u.id"),
        ColumnReference(name="u.name"),
        ColumnReference(name="u.email"),
        ColumnReference(name="u.age"),
        ColumnReference(name="status")  # Simplified for this example
    ]],
    where_clause=BinaryExpression(
        left=BinaryExpression(
            left=ColumnReference(name="u.email"),
            operator="IS NOT NULL",
            right=Literal(value=None, type="null")
        ),
        operator="AND",
        right=BinaryExpression(
            left=ColumnReference(name="u.name"),
            operator="IS NOT NULL",
            right=Literal(value=None, type="null")
        )
    )
)
```

## Limitations and Future Enhancements

### Current Limitations

1. **No Subqueries**: The parser does not support subqueries in SELECT, WHERE, or FROM clauses
2. **Limited JOINs**: Only basic table references are supported, not explicit JOIN syntax
3. **No Window Functions**: Window functions like ROW_NUMBER(), RANK() are not supported
4. **No CTEs**: Common Table Expressions (WITH clause) are not supported
5. **Limited Data Types**: Complex data types like JSON, ARRAY are not supported
6. **No Stored Procedures**: Function and procedure definitions are not supported

### Planned Enhancements

1. **Subquery Support**: Add support for subqueries in various clauses
2. **JOIN Syntax**: Implement explicit JOIN syntax (INNER, LEFT, RIGHT, FULL)
3. **Window Functions**: Add support for window functions and OVER clause
4. **CTEs**: Implement Common Table Expressions
5. **Advanced Data Types**: Support for JSON, ARRAY, and other complex types
6. **Index and Constraint Support**: Enhanced DDL for indexes and constraints

## Performance Considerations

- The PLY parser generates efficient LALR(1) parsing tables
- Lexer tokens are cached for repeated parsing operations
- AST nodes are lightweight and memory-efficient
- Error recovery is minimal to maintain parsing performance
- Large queries are parsed incrementally to manage memory usage
