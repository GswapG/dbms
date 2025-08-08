# Logging API Reference

The DBMS project uses a centralized logging system with automatic class name detection and module-specific loggers.

## Logger Setup

All logging configuration is centralized in `src/common/logging_config.py`. The system automatically initializes when modules are imported.

```python
from dbms.common.logging_config import get_logger

# Get a module-specific logger
logger = get_logger("storage")
logger.info("Message")
logger.error("Error message")
```

## Module-Specific Loggers

Each major component has its own logger:

- **Storage**: `dbms.storage`
- **Parser**: `dbms.parser`
- **Executor**: `dbms.executor`
- **Client**: `dbms.client`
- **Common**: `dbms.common`

## Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about program execution
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for serious problems

## Automatic Class Name Detection

The logging system automatically detects class names from the calling context:

```python
class StorageEngine:
    def __init__(self):
        self.logger = get_logger("storage")

    def create_database(self, name: str):
        # Class name "StorageEngine" is automatically detected
        self.logger.info(f"Creating database: {name}")
```

## Log Format

Log entries follow this format:

```
[timestamp] LEVEL [module.class_name.function_name] message
```

Example:
```
[2025-07-26 06:08:07,307] INFO [dbms.storage.StorageEngine.create_database] Creating database: test_db
```

## Configuration

The logging system can be configured with different options:

```python
from dbms.common.logging_config import setup_logging

setup_logging(
    log_file="custom.log",
    log_level=logging.DEBUG,
    enable_console=True
)
```

## Usage in Modules

All components use their respective module loggers:

```python
# In storage module
from dbms.common.logging_config import get_logger
logger = get_logger("storage")

# In parser module
from dbms.common.logging_config import get_logger
logger = get_logger("parser")

# In executor module
from dbms.common.logging_config import get_logger
logger = get_logger("executor")
```

## Example Log Messages

```
[2025-07-26 06:08:07,307] INFO [dbms.storage.StorageEngine.create_database] Creating database: test_db
[2025-07-26 06:08:07,335] INFO [dbms.parser.PLYParser.parse] Parsing SQL: SELECT * FROM users WHERE age > 30
[2025-07-26 06:08:07,341] INFO [dbms.executor.Executor.execute_query] Executing query: SELECT * FROM users
```

## Log File Location

By default, all logs are written to `dbms_backend.log` in the project root.

## Related Documentation

- **[Logging Strategy](../explanation/logging.md)**: Detailed logging design and usage
- **[Configuration](../explanation/configuration.md)**: Global configuration settings
