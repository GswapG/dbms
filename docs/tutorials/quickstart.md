# Quick Start Guide

This tutorial will get you up and running with the DBMS in minutes. You'll learn how to install the system, run your first SQL query, and understand the basic workflow.

## Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)

## Step 1: Clone and Install

1. **Clone the repository**:
   ```bash
   git clone https://github.com/GswapG/dbms.git
   cd dbms
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   ```bash
   # On Windows
   .venv\Scripts\activate

   # On Linux/Mac
   source .venv/bin/activate
   ```

4. **Install the package**:
   ```bash
   python -m pip install -e .
   ```

## Step 2: Verify Installation

Run the test suite to ensure everything is working:

```bash
# On Windows
.\run_tests.ps1

# On Linux/Mac
./run_tests.sh
```

You should see output indicating that tests are passing.

## Step 3: Your First SQL Query

Create a Python script or use the interactive Python shell:

```python
from dbms.parser.parser import PLYParser

# Create a parser instance
parser = PLYParser()

# Parse a simple SQL query
sql = "SELECT name, age FROM users WHERE age > 18"
ast = parser.parse(sql)

# Examine the parsed result
print(f"Query type: {type(ast.statement).__name__}")
print(f"Table: {ast.statement.from_clause}")
print(f"Columns: {[col.name for col in ast.statement.columns]}")
```

## Step 4: Explore the AST

The parser generates an Abstract Syntax Tree (AST) that represents your SQL query:

```python
# Access the WHERE clause
where_clause = ast.statement.where_clause
print(f"Where condition: {where_clause.operator} {where_clause.right.value}")

# Check if it's a comparison
if hasattr(where_clause, 'left'):
    print(f"Comparing: {where_clause.left.name} {where_clause.operator} {where_clause.right.value}")
```

## Step 5: Try Different Queries

Experiment with different SQL statements:

```python
# INSERT statement
insert_sql = "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')"
insert_ast = parser.parse(insert_sql)

# CREATE TABLE statement
create_sql = """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price FLOAT
)
"""
create_ast = parser.parse(create_sql)

# Complex SELECT with functions
complex_sql = """
SELECT department, COUNT(*) as emp_count, AVG(salary) as avg_salary
FROM employees
WHERE status = 'active'
GROUP BY department
HAVING COUNT(*) > 5
ORDER BY avg_salary DESC
LIMIT 10
"""
complex_ast = parser.parse(complex_sql)
```

## Step 6: Visualize Parse Trees (Optional)

Enable parse tree visualization to see how your queries are parsed:

```python
from dbms.common import config

# Enable visualization
config.generate_parse_tree_images = True

# Parse a query - this will generate a visual parse tree
sql = "SELECT name, age FROM users WHERE age > 30"
ast = parser.parse(sql)
```

Parse tree images will be saved in the `parse_trees/` directory.

## What's Next?

Now that you have the basics working, you can:

- **[First SQL Query](first-query.md)**: Learn more about writing and executing SQL queries
- **[Building Complex Queries](complex-queries.md)**: Explore advanced SQL features
- **[Debugging Queries](../how-to/debugging.md)**: Learn how to troubleshoot parsing issues
- **[Extending the Parser](../how-to/extending-parser.md)**: Add new SQL features

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you've activated the virtual environment
2. **Test Failures**: Ensure all dependencies are installed correctly
3. **Parse Errors**: Check your SQL syntax - the parser provides detailed error messages

### Getting Help

- Check the [API Reference](../api/parser.md) for detailed class and method documentation
- Review the [SQL Parser Deep Dive](../explanation/parser.md) for implementation details
- Look at the test files in `tests/unit/test_parser.py` for examples

---

**Congratulations!** You've successfully set up the DBMS and parsed your first SQL query. You're ready to explore more advanced features and start building your own database applications.
