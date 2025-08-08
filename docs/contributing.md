# Contributing

Thank you for your interest in contributing to the DBMS project!

## Code Style
- Use [black](https://github.com/psf/black) for code formatting.
- Type annotations are required; use [mypy](http://mypy-lang.org/) for type checking.

## Testing
- Write tests for all new features and bug fixes.
- Use `pytest` for unit and integration tests.
- Run all tests with `run_tests.sh` (Linux/Mac) or `run_tests.ps1` (Windows) before submitting a PR.

## Documentation
- Update or add Markdown docs in the `docs/` directory as needed.
- Use relative links to connect related docs.
- Keep documentation up to date with code changes.

## Logging
- Use module-specific loggers from `dbms.common.logging_config` for all backend logs.
- Get loggers using `get_logger("module_name")` (e.g., `get_logger("storage")`).
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR).
- Class names are automatically detected - no need to include them manually in messages.
- Follow the pattern: `logger.info("Clean message without hardcoded class names")`

## Related Docs
- [Logging](explanation/logging.md)
- [Storage Backend](explanation/storage.md)
