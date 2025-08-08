"""Common utilities and error types for DBMS."""

from .errors import (
    DBMSError,
    StorageError,
    DatabaseError,
    TableError,
    ValidationError,
    ParserError,
    ExecutorError,
    DatabaseNotFoundError,
    DatabaseExistsError,
    TableNotFoundError,
    TableExistsError,
    SchemaError,
    DataTypeError,
)

# Import logging configuration to ensure it's set up
from . import logging_config
