#!/bin/bash

# Exit on any error
set -e

# Function to print headers
print_header() {
    echo -e "\n=== $1 ===\n"
}

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    print_header "Activating virtual environment"
    source .venv/bin/activate
fi

# Run type checking
print_header "Running type checking"
mypy src tests

# Run code formatting
print_header "Running code formatting check"
if ! black --check .; then
    echo -e "\nCode formatting check failed! Running black to format code..."
    black .
fi

# Run tests with coverage
print_header "Running tests with coverage"
pytest tests/unit tests/integration --cov=src --cov-report=term-missing

echo -e "\nAll checks passed successfully!"
