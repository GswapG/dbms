# Logging Strategy

The DBMS project uses a centralized logging system that provides automatic class name detection and module-specific loggers for better debugging and monitoring.

## Overview

The logging system is designed to:
- **Automatically detect class names** from the calling context
- **Separate loggers by module** (storage, parser, executor, client)
- **Provide consistent formatting** across all components
- **Enable easy debugging** with detailed context information

## Architecture

### Centralized Configuration

All logging configuration is centralized in `src/common/logging_config.py`:

```python
from dbms.common.logging_config import get_logger

# Get a module-specific logger
logger = get_logger("storage")
```

### Module-Specific Loggers

Each major component has its own logger:

- **Storage**: `dbms.storage`
- **Parser**: `dbms.parser`
- **Executor**: `dbms.executor`
- **Client**: `dbms.client`
- **Common**: `dbms.common`

### Automatic Class Name Detection

The system automatically detects the class name from the calling context using a custom formatter:

```python
class StorageEngine:
    def __init__(self):
        self.logger = get_logger("storage")

    def create_database(self, name: str):
        # This will automatically show "StorageEngine" in the log
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

## Usage

### Basic Usage

```python
from dbms.common.logging_config import get_logger

# Get logger for your module
logger = get_logger("storage")

# Log messages (class name is automatically detected)
logger.info("Database created successfully")
logger.debug("Processing batch of 1000 records")
logger.warning("Table already exists")
logger.error("Failed to connect to database")
```

### In Classes

```python
class MyClass:
    def __init__(self):
        self.logger = get_logger("my_module")

    def my_method(self):
        # Class name "MyClass" will be automatically detected
        self.logger.info("Method executed successfully")
```

### Configuration

The logging system can be configured with different options:

```python
from dbms.common.logging_config import setup_logging

# Setup with custom options
setup_logging(
    log_file="custom.log",
    log_level=logging.DEBUG,
    enable_console=True
)
```

## Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about program execution
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for serious problems

## File Output

By default, all logs are written to `dbms_backend.log` in the project root. The log file includes:

- Timestamps for all entries
- Module and class context
- Function names where logs were generated
- Full message content

## Benefits

1. **Automatic Context**: No need to manually specify class names in log messages
2. **Module Separation**: Easy to filter logs by component
3. **Consistent Format**: Uniform logging format across all modules
4. **Easy Debugging**: Clear context for troubleshooting
5. **Performance**: Efficient logging with minimal overhead

## Migration from Old System

The old logging system used hardcoded class names in messages:

```python
# Old way (no longer needed)
logger.info(f"[StorageEngine] Creating database: {name}")
```

The new system automatically handles this:

```python
# New way (class name is automatic)
logger.info(f"Creating database: {name}")
```

## Testing

The logging system includes comprehensive tests in `tests/unit/test_logging.py` that verify:

- Module-specific logger creation
- Automatic class name detection
- Log file output
- Error handling

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `log_file` | `dbms_backend.log` | Path to log file |
| `log_level` | `INFO` | Minimum log level |
| `enable_console` | `False` | Whether to also log to console |

## Best Practices

1. **Use appropriate log levels**: DEBUG for detailed info, INFO for general flow, WARNING for issues, ERROR for problems
2. **Include context**: Log relevant data like IDs, names, or counts
3. **Avoid sensitive data**: Never log passwords, tokens, or personal information
4. **Use structured messages**: Make log messages parseable and meaningful
5. **Test logging**: Ensure your logging works in test environments
