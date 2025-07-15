# dbms
[![Tests](https://github.com/GswapG/dbms/actions/workflows/tests.yml/badge.svg)](https://github.com/GswapG/dbms/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/GswapG/dbms/branch/main/graph/badge.svg)](https://codecov.io/gh/GswapG/dbms)

Learning 3. To run all tests and checks:

   Windows (PowerShell):
   ```powershell
   .\run_tests.ps1
   ```

   Unix-like systems:
   ```bash
   ./run_tests.sh
   ```

   This will run:
   - Type checking (mypy)
   - Code formatting check (black)
   - Tests with coverage report (pytest)

4. To run just the tests with coverage:
   ```bash
   pytest --cov=src
   ```

### Test Structurenternals through hands on project

## Testing

This project uses pytest for automated testing. To run the tests:

1. Make sure you have all development dependencies installed:
   ```bash
   python -m pip install -r requirements-dev.txt
   ```

2. Run the tests:
   ```bash
   pytest
   ```

3. To run tests with coverage report:
   ```bash
   pytest --cov=src
   ```

### Test Structure

- Unit tests are located in `tests/` directory
- Each component has its own test file (e.g., `test_storage.py`, `test_parser.py`)
- Integration tests will be added in `tests/integration/`
- System tests will be added in `tests/system/`

### Writing Tests

When adding new features:
1. Create corresponding test file if it doesn't exist
2. Add test cases before implementing the feature (TDD approach)
3. Ensure tests cover both success and error cases
4. Add integration tests if the feature interacts with other components
