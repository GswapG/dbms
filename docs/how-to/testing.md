# Running Tests

This guide covers how to run the DBMS test suite, understand test results, and write new tests.

## Quick Start

### Run All Tests

```bash
# On Windows
.\run_tests.ps1

# On Linux/macOS
./run_tests.sh
```

This command runs:
- Code formatting (black)
- Type checking (mypy)
- Tests with coverage (pytest)

### Run Tests Only

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/unit/test_parser.py

# Run specific test function
python -m pytest tests/unit/test_parser.py::test_select_statement
```

## Test Structure

### Test Organization

```
tests/
├── unit/                    # Unit tests
│   ├── test_parser.py      # Parser tests
│   ├── test_storage.py     # Storage tests
│   └── test_executor.py    # Executor tests
├── integration/            # Integration tests
│   └── test_storage.py     # End-to-end storage tests
└── sample_data/            # Test data files
    ├── users.csv
    └── orders.csv
```

### Test Categories

**Unit Tests**: Test individual components in isolation
- Parser tests: SQL parsing functionality
- Storage tests: File operations and data management
- Executor tests: Query execution logic

**Integration Tests**: Test component interactions
- End-to-end query processing
- File system operations
- Error handling across components

## Running Specific Tests

### Parser Tests

```bash
# Run all parser tests
python -m pytest tests/unit/test_parser.py -v

# Run specific test categories
python -m pytest tests/unit/test_parser.py::test_select_statements -v
python -m pytest tests/unit/test_parser.py::test_insert_statements -v
python -m pytest tests/unit/test_parser.py::test_error_handling -v

# Run tests matching a pattern
python -m pytest tests/unit/test_parser.py -k "select" -v
```

### Storage Tests

```bash
# Run storage tests
python -m pytest tests/unit/test_storage.py -v

# Run integration tests
python -m pytest tests/integration/test_storage.py -v
```

### Coverage Reports

```bash
# Run tests with coverage
python -m pytest --cov=dbms --cov-report=term-missing

# Generate HTML coverage report
python -m pytest --cov=dbms --cov-report=html

# Generate XML coverage report (for CI/CD)
python -m pytest --cov=dbms --cov-report=xml
```

## Understanding Test Results

### Test Output

```
============================= test session starts ==============================
platform linux -- Python 3.11.5, pytest-7.4.0, pluggy-1.2.0
rootdir: /path/to/dbms
plugins: cov-4.1.0
collected 150 items

tests/unit/test_parser.py::test_select_statement PASSED              [  0%]
tests/unit/test_parser.py::test_insert_statement PASSED              [  1%]
tests/unit/test_parser.py::test_update_statement PASSED              [  2%]
...
tests/unit/test_parser.py::test_error_handling PASSED                [ 99%]
tests/unit/test_parser.py::test_performance PASSED                   [100%]

============================== 150 passed in 2.34s ==============================
```

### Coverage Report

```
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
src/parser/parser.py             245      0   100%
src/storage/storage.py           180      5    97%   45-49
src/executor/executor.py         120      0   100%
------------------------------------------------------------
TOTAL                           545      5    99%
```

**Understanding Coverage**:
- **Stmts**: Total statements in the file
- **Miss**: Statements not executed by tests
- **Cover**: Percentage of statements covered
- **Missing**: Line numbers of uncovered statements

## Writing New Tests

### Test File Structure

```python
import pytest
from dbms.parser.parser import PLYParser

class TestNewFeature:
    """Test class for new feature."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PLYParser()

    def test_basic_functionality(self):
        """Test basic functionality of new feature."""
        sql = "SELECT * FROM test_table"
        ast = self.parser.parse(sql)
        assert ast is not None
        assert ast.statement.from_clause == "test_table"

    def test_edge_case(self):
        """Test edge case handling."""
        # Test implementation
        pass

    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ParserError):
            self.parser.parse("INVALID SQL")
```

### Test Naming Conventions

- **Test files**: `test_<module>.py`
- **Test classes**: `Test<Feature>`
- **Test methods**: `test_<description>`

### Test Data

Use the sample data files for realistic testing:

```python
import os
from pathlib import Path

def test_with_sample_data():
    """Test using sample data files."""
    sample_data_dir = Path("tests/sample_data")
    users_file = sample_data_dir / "users.csv"

    assert users_file.exists()
    # Test implementation using sample data
```

## Debugging Failed Tests

### Verbose Output

```bash
# Run with maximum verbosity
python -m pytest tests/unit/test_parser.py::test_failing_test -vvv

# Show local variables on failure
python -m pytest tests/unit/test_parser.py::test_failing_test -l
```

### Debugging with pdb

```python
def test_debug_example():
    """Example of debugging a test."""
    import pdb; pdb.set_trace()  # Breakpoint
    sql = "SELECT * FROM users"
    ast = self.parser.parse(sql)
    # Continue debugging
```

### Common Test Issues

**Import Errors**:
```bash
# Ensure package is installed in development mode
python -m pip install -e .
```

**File Path Issues**:
```python
# Use relative paths from project root
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
data_file = project_root / "tests" / "sample_data" / "users.csv"
```

**Test Isolation**:
```python
def setup_method(self):
    """Reset state between tests."""
    self.parser.reset()
```

## Continuous Integration

### GitHub Actions

The project uses GitHub Actions for automated testing:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install -e .
          python -m pip install pytest pytest-cov
      - name: Run tests
        run: python -m pytest --cov=dbms --cov-report=xml
```

### Pre-commit Hooks

Install pre-commit hooks for automatic testing:

```bash
# Install pre-commit
python -m pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Performance Testing

### Benchmark Tests

```python
import time
import pytest

def test_parser_performance():
    """Test parser performance with large queries."""
    start_time = time.time()

    # Generate large query
    large_query = "SELECT " + ", ".join([f"col{i}" for i in range(100)]) + " FROM large_table"

    # Parse query
    ast = self.parser.parse(large_query)

    end_time = time.time()
    parse_time = end_time - start_time

    # Assert reasonable performance
    assert parse_time < 1.0  # Should parse in under 1 second
    assert ast is not None
```

### Memory Usage Tests

```python
import psutil
import os

def test_memory_usage():
    """Test memory usage during parsing."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    # Parse multiple queries
    for i in range(100):
        sql = f"SELECT * FROM table{i}"
        ast = self.parser.parse(sql)

    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory

    # Assert reasonable memory usage
    assert memory_increase < 50 * 1024 * 1024  # Less than 50MB increase
```

## Best Practices

### Test Organization

1. **Group related tests** in test classes
2. **Use descriptive test names** that explain what is being tested
3. **Keep tests independent** - each test should be able to run in isolation
4. **Use fixtures** for common setup code

### Test Data Management

1. **Use sample data files** for realistic testing
2. **Create test-specific data** when needed
3. **Clean up test data** after tests complete
4. **Don't modify production data** in tests

### Assertion Best Practices

```python
# Good assertions
assert ast.statement.from_clause == "users"
assert len(ast.statement.columns) == 2
assert isinstance(ast.statement, SelectStatement)

# Avoid complex assertions
# Bad: assert str(ast).contains("users")
# Good: assert ast.statement.from_clause == "users"
```

## Related Documentation

- **[Installation Guide](installation.md)**: Set up the development environment
- **[Debugging Queries](debugging.md)**: Troubleshoot parsing issues
- **[API Reference](../api/parser.md)**: Complete API documentation
- **[Contributing Guide](../contributing.md)**: Development guidelines

---

Testing is crucial for maintaining code quality and preventing regressions. This guide should help you run tests effectively and contribute to the test suite.
