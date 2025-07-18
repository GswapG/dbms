# Logging

See [Configuration](configuration.md) for details on global settings (log file, etc.).

This document describes the logging strategy for the DBMS backend.

## Log File
- All backend logs are written to `dbms_backend.log` in the project root.
- The logger is configured at the DEBUG level by default.

## Log Format
- Each log entry includes a timestamp, log level, logger name, function name, and message.
- Example:
  ```
  [2024-06-01 12:34:56,789] INFO [dbms.create_database] [StorageEngine] Database 'test_db' created with UID 1234abcd-...
  ```

## Log Levels
- `DEBUG`: Detailed information for debugging.
- `INFO`: High-level events (e.g., database/table creation).
- `WARNING`: Potential issues (e.g., duplicate creation attempts).
- `ERROR`: Errors and exceptions.

## Logger Usage
- All backend modules use the same global logger (`dbms`).
- Log messages should indicate which object/class is generating the log.

## Related Docs
- [Storage Backend](./storage.md)
- [Architecture Overview](./architecture.md)
