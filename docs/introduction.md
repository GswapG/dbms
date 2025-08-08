# DBMS Documentation

Welcome to the DBMS documentation! This project implements a SQL-compliant database from scratch, providing hands-on learning of database management system internals.

## What is DBMS?

DBMS is a complete database management system that demonstrates core database concepts through implementation. It includes:

- **SQL Parser**: Full SQL parsing with PLY (Python Lex-Yacc)
- **Storage Engine**: File-based data storage with CSV format
- **Query Executor**: SQL query execution engine
- **Logging System**: Comprehensive logging for debugging and monitoring

## Documentation Structure

Our documentation follows the [Diátaxis methodology](https://docs.divio.com/documentation-system/) with four distinct types:

### 🚀 **Tutorials** - Getting Started
Learn how to use the DBMS step by step:

- **[Quick Start Guide](tutorials/quickstart.md)**: Get up and running in minutes
- **[First SQL Query](tutorials/first-query.md)**: Write and execute your first SQL query
- **[Building Complex Queries](tutorials/complex-queries.md)**: Learn advanced SQL features

### 🔧 **How-to Guides** - Task-Oriented
Complete specific tasks and solve problems:

- **[Installation Guide](how-to/installation.md)**: Set up the development environment
- **[Running Tests](how-to/testing.md)**: Execute the test suite and understand results
- **[Debugging Queries](how-to/debugging.md)**: Troubleshoot SQL parsing issues
- **[Extending the Parser](how-to/extending-parser.md)**: Add new SQL features
- **[Parse Tree Visualization](how-to/parse-trees.md)**: Generate and interpret parse trees

### 📚 **Reference** - API Documentation
Complete technical reference for all components:

- **[Parser API](api/parser.md)**: SQL parser classes and methods
- **[Storage API](api/storage.md)**: Data storage and file management
- **[Executor API](api/executor.md)**: Query execution engine
- **[Logging API](api/logging.md)**: Logging configuration and usage
- **[Client API](api/client.md)**: Client interface and communication

### 📖 **Explanation** - Conceptual Documentation
Understand the concepts and architecture:

- **[Architecture Overview](explanation/architecture.md)**: System design and data flow
- **[SQL Parser Deep Dive](explanation/parser.md)**: How SQL parsing works
- **[Grammar Reference](explanation/grammar.md)**: Complete SQL grammar specification
- **[Storage System](explanation/storage.md)**: Data storage and file formats
- **[Query Execution](explanation/execution.md)**: How queries are processed
- **[Configuration](explanation/configuration.md)**: System configuration options
- **[Logging Strategy](explanation/logging.md)**: Logging design and usage

## Key Features

### 🎯 **SQL Parser**
- **Comprehensive SQL Support**: SELECT, INSERT, UPDATE, DELETE, CREATE, DROP
- **Complex Expressions**: Arithmetic, logical, and comparison operators
- **Aggregate Functions**: COUNT, SUM, AVG, MAX, MIN
- **Visual Debugging**: Parse tree visualization with Graphviz
- **Error Handling**: Detailed syntax error reporting

### 💾 **Storage Engine**
- **CSV-based Storage**: Simple, human-readable data format
- **CRUD Operations**: Create, Read, Update, Delete operations
- **Metadata Management**: Table and database metadata storage
- **File Management**: Efficient file handling and organization

### ⚡ **Query Executor**
- **AST Processing**: Execute parsed SQL statements
- **Result Generation**: Format and return query results
- **Error Handling**: Graceful error recovery and reporting

### 📊 **Development Tools**
- **Comprehensive Testing**: 100+ test cases with coverage reporting
- **Logging System**: Detailed logging for debugging
- **Documentation**: Complete API and conceptual documentation

## Quick Start

1. **Install Dependencies**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   python -m pip install -e .
   ```

2. **Run Tests**:
   ```bash
   # Windows
   .\run_tests.ps1

   # Linux/Mac
   ./run_tests.sh
   ```

3. **Parse Your First Query**:
   ```python
   from dbms.parser.parser import PLYParser

   parser = PLYParser()
   sql = "SELECT name, age FROM users WHERE age > 18"
   ast = parser.parse(sql)
   print(f"Parsed: {type(ast.statement).__name__}")
   ```

## Project Structure

```
dbms/
├── src/                    # Source code
│   ├── parser/            # SQL parser implementation
│   ├── storage/           # Data storage engine
│   ├── executor/          # Query execution engine
│   └── common/            # Shared utilities
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                  # Documentation
│   ├── tutorials/         # Getting started guides
│   ├── how-to/           # Task-oriented guides
│   ├── api/              # API reference
│   └── explanation/      # Conceptual documentation
└── manual_db/            # Sample database files
```

## Contributing

We welcome contributions! See our [Contributing Guide](contributing.md) for details on:

- Code style and conventions
- Testing requirements
- Documentation standards
- Pull request process

## External Resources

- **[PLY Documentation](https://www.dabeaz.com/ply/)**: Python Lex-Yacc implementation
- **[SQL Standard](https://www.iso.org/standard/63555.html)**: ISO/IEC 9075 SQL standard
- **[Graphviz](https://graphviz.org/)**: Parse tree visualization
- **[Diátaxis Documentation System](https://docs.divio.com/documentation-system/)**: Documentation methodology

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

---

**Ready to get started?** Begin with the [Quick Start Guide](tutorials/quickstart.md) or explore the [Architecture Overview](explanation/architecture.md) to understand the system design.
