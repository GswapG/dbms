# Query Execution

This document explains how SQL queries are executed in the DBMS, from parsing to result generation.

## Overview

Query execution in the DBMS follows a multi-stage pipeline:

1. **SQL Parsing**: Convert SQL text to Abstract Syntax Tree (AST)
2. **Query Planning**: Analyze and optimize the execution plan
3. **Execution**: Execute the plan against the storage engine
4. **Result Generation**: Format and return results

## Execution Pipeline

### Stage 1: SQL Parsing

The first stage converts human-readable SQL into a structured representation:

```python
from dbms.parser.parser import PLYParser

parser = PLYParser()
sql = "SELECT name, age FROM users WHERE age > 18"
ast = parser.parse(sql)
```

**What happens:**
- **Lexical Analysis**: SQL text is tokenized into keywords, identifiers, operators, etc.
- **Syntax Analysis**: Tokens are parsed according to SQL grammar rules
- **AST Generation**: A tree structure representing the query is created

**Output**: `SQLStatement` object containing the parsed query structure

### Stage 2: Query Planning

The query planner analyzes the AST and creates an execution plan:

```python
# The executor analyzes the AST to determine:
# - Which tables need to be accessed
# - What filters to apply
# - How to join multiple tables (if applicable)
# - What aggregations to perform
# - How to sort and limit results
```

**Planning Decisions:**
- **Table Access**: Determine which tables and files to read
- **Filter Application**: Identify WHERE clause conditions
- **Join Strategy**: Plan how to combine multiple tables
- **Aggregation**: Plan GROUP BY and aggregate functions
- **Sorting**: Plan ORDER BY operations
- **Limiting**: Plan LIMIT and OFFSET operations

### Stage 3: Execution

The executor carries out the planned operations:

```python
from dbms.executor.executor import QueryExecutor

executor = QueryExecutor()
result = executor.execute(ast)
```

**Execution Steps:**
1. **Table Scan**: Read data from CSV files
2. **Filtering**: Apply WHERE conditions
3. **Projection**: Select required columns
4. **Aggregation**: Apply GROUP BY and aggregate functions
5. **Sorting**: Apply ORDER BY
6. **Limiting**: Apply LIMIT and OFFSET

### Stage 4: Result Generation

The final stage formats and returns results:

```python
# Results are formatted as:
{
    "columns": ["name", "age"],
    "rows": [
        ["Alice", 25],
        ["Bob", 30],
        ["Charlie", 22]
    ],
    "row_count": 3
}
```

## Storage Integration

### File-Based Storage

The DBMS uses CSV files for data storage:

```
manual_db/
├── users.csv          # Table data
├── orders.csv         # Table data
└── metadata.json      # Schema information
```

### Data Access Patterns

**Sequential Scan**: For simple queries, the executor reads entire CSV files:
```python
# For: SELECT * FROM users
with open('manual_db/users.csv', 'r') as f:
    for line in f:
        # Process each row
        pass
```

**Filtered Scan**: Apply WHERE conditions during file reading:
```python
# For: SELECT * FROM users WHERE age > 18
with open('manual_db/users.csv', 'r') as f:
    for line in f:
        row = parse_csv_line(line)
        if row['age'] > 18:  # Apply filter
            results.append(row)
```

## Query Types and Execution

### SELECT Queries

**Simple SELECT**:
```sql
SELECT name, age FROM users
```
**Execution**:
1. Read `users.csv` file
2. Extract `name` and `age` columns
3. Return all rows

**SELECT with WHERE**:
```sql
SELECT name, age FROM users WHERE age > 18
```
**Execution**:
1. Read `users.csv` file
2. For each row, evaluate `age > 18`
3. Include row only if condition is true
4. Extract `name` and `age` columns

**SELECT with Aggregation**:
```sql
SELECT department, COUNT(*) FROM employees GROUP BY department
```
**Execution**:
1. Read `employees.csv` file
2. Group rows by `department` value
3. Count rows in each group
4. Return department and count pairs

### INSERT Queries

```sql
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')
```
**Execution**:
1. Validate table exists
2. Check column constraints
3. Append new row to CSV file
4. Update metadata if needed

### UPDATE Queries

```sql
UPDATE users SET age = 25 WHERE name = 'Alice'
```
**Execution**:
1. Read entire CSV file
2. For each row, check WHERE condition
3. If condition matches, update specified columns
4. Write modified data back to file

### DELETE Queries

```sql
DELETE FROM users WHERE age < 18
```
**Execution**:
1. Read entire CSV file
2. Filter out rows matching WHERE condition
3. Write remaining rows back to file

## Performance Considerations

### Memory Usage

**Small Tables**: Entire table can fit in memory
```python
# Load entire table into memory
with open('small_table.csv', 'r') as f:
    data = [parse_row(line) for line in f]
```

**Large Tables**: Process row by row to minimize memory usage
```python
# Process one row at a time
with open('large_table.csv', 'r') as f:
    for line in f:
        row = parse_row(line)
        process_row(row)
```

### Optimization Strategies

**Indexing**: Future enhancement for faster lookups
```python
# Conceptual index structure
index = {
    "age": {
        18: [row_ids],
        25: [row_ids],
        30: [row_ids]
    }
}
```

**Query Caching**: Cache frequently executed queries
```python
# Cache parsed ASTs and execution plans
query_cache = {
    "SELECT * FROM users": cached_plan,
    "SELECT name FROM users WHERE age > 18": cached_plan
}
```

## Error Handling

### Parsing Errors

```python
try:
    ast = parser.parse("SELECT * FROM users WHERE age >")
except ParserError as e:
    # Handle syntax errors
    print(f"Syntax error: {e}")
```

### Execution Errors

```python
try:
    result = executor.execute(ast)
except ExecutionError as e:
    # Handle execution errors
    print(f"Execution error: {e}")
```

**Common Errors**:
- **Table Not Found**: Referenced table doesn't exist
- **Column Not Found**: Referenced column doesn't exist
- **Type Mismatch**: Data type conflicts in operations
- **Constraint Violation**: Data violates table constraints

## Future Enhancements

### Query Optimization

**Cost-Based Optimization**: Choose best execution plan based on:
- Table sizes
- Data distribution
- Available indexes
- Query complexity

**Parallel Execution**: Execute parts of queries in parallel:
```python
# Split large table into chunks
chunks = split_table_into_chunks(table, num_workers)
results = parallel_map(process_chunk, chunks)
```

### Advanced Features

**Transactions**: Support for ACID properties
**Indexing**: B-tree and hash indexes for faster lookups
**Views**: Virtual tables based on queries
**Stored Procedures**: Pre-compiled query sequences

## Related Documentation

- **[Storage System](storage.md)**: How data is stored and accessed
- **[Parser Deep Dive](parser.md)**: How SQL parsing works
- **[Executor API](../api/executor.md)**: Complete executor API reference
- **[Architecture Overview](architecture.md)**: Overall system design

---

Query execution is the core of any database system. Understanding how queries flow from SQL text to results helps in optimizing performance and debugging issues.
