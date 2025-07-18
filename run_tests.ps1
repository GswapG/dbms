#!/usr/bin/env pwsh

# Script to run tests and code quality checks
$ErrorActionPreference = "Stop"

function Write-Header {
    param($message)
    Write-Host "`n=== $message ===`n" -ForegroundColor Cyan
}

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Header "Activating virtual environment"
    .\.venv\Scripts\Activate.ps1
}

# Run type checking on source code
Write-Header "Running type checking"
mypy src

if ($LASTEXITCODE -ne 0) {
    Write-Host "Type checking failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

# Run code formatting
Write-Header "Running code formatting check"
black --check .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Code formatting check failed! Running black to format code..." -ForegroundColor Yellow
    black .
}

# Run tests with coverage
Write-Header "Running tests with coverage"
pytest tests/unit tests/integration --cov=src --cov-report=term-missing

if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nAll checks passed successfully!" -ForegroundColor Green
