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
- Use the global logger (`dbms`) for all backend logs.
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR).
- Include context (e.g., class or function name) in log messages.

## Related Docs
- [Logging](./logging.md)
- [Storage Backend](./storage.md)
