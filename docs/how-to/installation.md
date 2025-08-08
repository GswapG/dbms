# Installation Guide

This guide covers how to set up the DBMS development environment on different operating systems.

## System Requirements

- **Python**: 3.8 or higher
- **Git**: For version control
- **Memory**: At least 2GB RAM
- **Disk Space**: 100MB for the project and dependencies

## Operating System Setup

### Windows

1. **Install Python**:
   - Download Python from [python.org](https://www.python.org/downloads/)
   - Ensure "Add Python to PATH" is checked during installation
   - Verify installation: `python --version`

2. **Install Git**:
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Use default settings during installation

3. **Install Visual Studio Build Tools** (if needed):
   - Required for some Python packages with C extensions
   - Download from Microsoft Visual Studio website

### macOS

1. **Install Python**:
   ```bash
   # Using Homebrew (recommended)
   brew install python

   # Or download from python.org
   ```

2. **Install Git**:
   ```bash
   brew install git
   ```

3. **Install Xcode Command Line Tools**:
   ```bash
   xcode-select --install
   ```

### Linux (Ubuntu/Debian)

1. **Update package list**:
   ```bash
   sudo apt update
   ```

2. **Install Python and Git**:
   ```bash
   sudo apt install python3 python3-pip python3-venv git
   ```

3. **Install build dependencies**:
   ```bash
   sudo apt install build-essential python3-dev
   ```

## Project Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/GswapG/dbms.git
cd dbms
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install the package in development mode
python -m pip install -e .

# Install additional development dependencies
python -m pip install pytest pytest-cov black mypy
```

### Step 4: Install Optional Dependencies

For parse tree visualization:

```bash
# Install Graphviz
# On Windows:
# Download from https://graphviz.org/download/

# On macOS:
brew install graphviz

# On Ubuntu/Debian:
sudo apt install graphviz

# Install Python Graphviz package
python -m pip install graphviz
```

## Verification

### Run Tests

```bash
# On Windows
.\run_tests.ps1

# On Linux/macOS
./run_tests.sh
```

### Manual Verification

```python
# Test basic functionality
from dbms.parser.parser import PLYParser

parser = PLYParser()
sql = "SELECT * FROM users"
ast = parser.parse(sql)
print("Parser is working correctly!")
```

## Development Tools Setup

### Code Formatting

The project uses `black` for code formatting:

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

### Type Checking

The project uses `mypy` for static type checking:

```bash
# Run type checking
mypy src/

# Run with strict mode
mypy --strict src/
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
# Install pre-commit
python -m pip install pre-commit

# Install the git hook scripts
pre-commit install
```

## IDE Setup

### VS Code

1. **Install Python extension**
2. **Configure Python interpreter**:
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
   - Type "Python: Select Interpreter"
   - Choose the interpreter from `.venv/bin/python`

3. **Recommended extensions**:
   - Python
   - Pylance
   - GitLens
   - Python Test Explorer

### PyCharm

1. **Open the project**
2. **Configure Python interpreter**:
   - Go to File → Settings → Project → Python Interpreter
   - Add the virtual environment interpreter

3. **Configure run configurations** for tests

## Troubleshooting

### Common Issues

#### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'dbms'`

**Solution**: Ensure you're in the virtual environment and the package is installed:
```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Reinstall package
python -m pip install -e .
```

#### Permission Errors

**Problem**: Permission denied when installing packages

**Solution**: Use virtual environments instead of system-wide installation:
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

#### Graphviz Issues

**Problem**: `graphviz.backend.ExecutableNotFound`

**Solution**: Install Graphviz system package:
```bash
# On Ubuntu/Debian
sudo apt install graphviz

# On macOS
brew install graphviz

# On Windows: Download from https://graphviz.org/download/
```

#### Test Failures

**Problem**: Tests are failing after installation

**Solution**: Check dependencies and environment:
```bash
# Reinstall all dependencies
python -m pip install -r requirements.txt
python -m pip install -e .

# Run tests with verbose output
python -m pytest tests/ -v
```

### Getting Help

- Check the [Quick Start Guide](../tutorials/quickstart.md) for basic setup
- Review the [Contributing Guide](../contributing.md) for development guidelines
- Open an issue on GitHub for specific problems

## Next Steps

After successful installation:

1. **[Quick Start Guide](../tutorials/quickstart.md)**: Get up and running quickly
2. **[Running Tests](testing.md)**: Learn how to run and understand test results
3. **[Debugging Queries](debugging.md)**: Learn troubleshooting techniques
4. **[API Reference](../api/parser.md)**: Explore the complete API documentation

---

Your development environment is now ready! You can start exploring the DBMS codebase and contributing to the project.
