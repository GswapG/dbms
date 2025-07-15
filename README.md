# DBMS
[![Tests](https://github.com/GswapG/dbms/actions/workflows/tests.yml/badge.svg)](https://github.com/GswapG/dbms/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/GswapG/dbms/graphs/icicle.svg?token=N0E4MJHR2M)](https://codecov.io/gh/GswapG/dbms)

A hands-on project to learn DBMS internals by building a SQL-compliant database from scratch.

## Project Overview

This project implements a SQL database that follows ANSI SQL syntax and provides standard database features.

### Features (Planned)

1. Storage Engine
   - Page-based storage system
   - Buffer management
   - B-tree indexing
   - Transaction logging

2. Query Processing
   - SQL parser using Python PLY
   - Query optimizer
   - Execution engine

3. SQL Support
   - DDL (CREATE DATABASE, CREATE TABLE)
   - DML (SELECT, INSERT, UPDATE)
   - Basic constraints (PRIMARY KEY, NOT NULL)
   - Advanced features (JOIN, GROUP BY, ORDER BY)

### Implementation

- Frontend (Python)
  - Query parsing
  - Planning
  - Client connection management
  
- Backend (C++)
  - Query execution
  - Storage management
  - Index operations

## Development

## Getting Started

1. Clone the repository
   ```bash
   git clone https://github.com/GswapG/dbms.git
   cd dbms
   ```

2. Set up Python environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

3. Install development dependencies
   ```bash
   python -m pip install -e .
   ```

4. Install pre-commit hooks
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Testing

To run the test suite:

### Quick Start

Run all checks (recommended):
```bash
# Windows
.\run_tests.ps1

# Linux/Mac
./run_tests.sh
```

This runs:
- Code formatting (black)
- Type checking (mypy)
- Tests with coverage (pytest)

### Manual Testing

Individual components can be tested:

- Unit tests are located in `tests/` directory
- Each component has its own test file (e.g., `test_storage.py`, `test_parser.py`)
- Integration tests will be added in `tests/integration/`
- System tests will be added in `tests/system/`

### Writing Tests

1. Format code:
   ```bash
   black .
   ```

2. Type checking:
   ```bash
   mypy src
   ```

3. Run tests with coverage:
   ```bash
   pytest --cov=src/dbms
   ```

## Development Workflow

1. Create feature branch
   ```bash
   git checkout -b feature-name
   ```

2. Implement tests first (TDD)
   - Create/update test file
   - Write test cases
   - Run tests (should fail)

3. Implement feature
   - Write code
   - Run tests until they pass
   - Ensure coverage is maintained

4. Submit changes
   - Format code (`black .`)
   - Run all checks (`./run_tests.sh` or `.\run_tests.ps1`)
   - Create pull request

## Contributing

1. Fork the repository
2. Create your feature branch
3. Follow the development workflow
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
