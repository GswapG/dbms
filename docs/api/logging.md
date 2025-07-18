# Logging API Reference

See [Configuration](../configuration.md) for details on global settings (log file, etc.).

## Logger Setup

The global logger is named `dbms` and is configured in `src/storage/storage.py`.
All logs are written to `dbms_backend.log` in the project root.
The logger is set to DEBUG level by default.

```python
import logging
logger = logging.getLogger("dbms")
logger.info("Message")
logger.error("Error message")
```

## Log Levels

- **DEBUG**: Detailed information for debugging.
- **INFO**: High-level events (e.g., database/table creation, deletion).
- **WARNING**: Potential issues (e.g., duplicate creation attempts).
- **ERROR**: Errors and exceptions.

## Usage in Modules

All storage engine operations, CRUD, and errors are logged using the global logger.

## Example Log Messages

```
[2025-07-18 12:34:56,789] INFO [dbms.create_database] [StorageEngine] Database 'mydb' created with UID ...
[2025-07-18 12:35:01,123] ERROR [dbms.delete_table] [StorageEngine] Table 'users' not found in database 'mydb'.
```

## Log File Location

All logs are in `dbms_backend.log` in the project root.
