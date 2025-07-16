"""Common error types used across the DBMS."""


class DBMSError(Exception):
    """Base class for all DBMS errors."""


class StorageError(DBMSError):
    """Base class for storage related errors."""


class DatabaseError(StorageError):
    """Database related errors."""


class TableError(StorageError):
    """Table related errors."""


class ValidationError(DBMSError):
    """Data validation errors."""


class ParserError(DBMSError):
    """SQL parsing related errors."""


class ExecutorError(DBMSError):
    """Query execution related errors."""


# More specific errors
class DatabaseNotFoundError(DatabaseError):
    """Raised when trying to access a non-existent database."""


class DatabaseExistsError(DatabaseError):
    """Raised when trying to create a database that already exists."""


class TableNotFoundError(TableError):
    """Raised when trying to access a non-existent table."""


class TableExistsError(TableError):
    """Raised when trying to create a table that already exists."""


class SchemaError(ValidationError):
    """Schema validation errors."""


class DataTypeError(ValidationError):
    """Data type validation errors."""
