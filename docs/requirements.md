# Project Requirements

This page lists all dependencies required for development and building the DBMS project, including Python packages and system-level tools.

---

## Python Requirements

| Package      | Version      | Purpose                        |
|--------------|-------------|--------------------------------|
| python       | >=3.9,<3.12  | Core language                  |
| ply          | ^3.11        | Lex/Yacc parsing               |
| pytest       | ^7.0         | Testing framework (dev)        |
| pytest-cov   | ^4.0         | Test coverage (dev)            |
| black        | ^24.0        | Code formatting (dev)          |
| mypy         | ^1.0         | Static type checking (dev)     |
| types-PyYAML | latest       | Type stubs for PyYAML (dev)    |
| pyyaml       | ^6.0         | YAML config parsing            |

## System Requirements

| Tool      | Version      | Purpose                        |
|-----------|-------------|--------------------------------|
| graphviz  | latest      | Parse tree image generation     |

- **Graphviz** must be installed on the system for parse tree visualization to work. On Ubuntu, use `sudo apt-get install graphviz`. On Windows, download from [graphviz.org](https://graphviz.org/download/).

## Installing All Requirements

```bash
# Install Python requirements
pip install -r requirements.txt

# Install development requirements
pip install -r requirements-dev.txt

# Install Graphviz (Ubuntu)
sudo apt-get install graphviz

# Install Graphviz (macOS)
brew install graphviz

# Install Graphviz (Windows)
# Download and install from https://graphviz.org/download/
```

---

## Development vs Build Requirements

- **Build requirements**: Needed to run the DBMS (Python, ply, pyyaml)
- **Development requirements**: Needed for testing, formatting, and type checking (pytest, pytest-cov, black, mypy, types-PyYAML)

---

## See Also
- [Installation Guide](how-to/installation.md)
- [Configuration](explanation/configuration.md)
