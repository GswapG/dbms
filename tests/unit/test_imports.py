"""Test module imports and error class hierarchy."""

import pytest

from dbms.common import (
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


def test_error_hierarchy():
    """Test that error classes are properly subclassed."""
    assert issubclass(StorageError, DBMSError)
    assert issubclass(DatabaseError, StorageError)
    assert issubclass(TableError, StorageError)
    assert issubclass(ValidationError, DBMSError)
    assert issubclass(ParserError, DBMSError)
    assert issubclass(ExecutorError, DBMSError)

    # Test specific error classes
    assert issubclass(DatabaseNotFoundError, DatabaseError)
    assert issubclass(DatabaseExistsError, DatabaseError)
    assert issubclass(TableNotFoundError, TableError)
    assert issubclass(TableExistsError, TableError)
    assert issubclass(SchemaError, ValidationError)
    assert issubclass(DataTypeError, ValidationError)


def test_error_instantiation():
    """Test that all error classes can be instantiated with a message."""
    msg = "Test error message"

    # Test base errors
    assert str(DBMSError(msg)) == msg
    assert str(StorageError(msg)) == msg
    assert str(DatabaseError(msg)) == msg
    assert str(TableError(msg)) == msg
    assert str(ValidationError(msg)) == msg
    assert str(ParserError(msg)) == msg
    assert str(ExecutorError(msg)) == msg

    # Test specific errors
    assert str(DatabaseNotFoundError(msg)) == msg
    assert str(DatabaseExistsError(msg)) == msg
    assert str(TableNotFoundError(msg)) == msg
    assert str(TableExistsError(msg)) == msg
    assert str(SchemaError(msg)) == msg
    assert str(DataTypeError(msg)) == msg


def test_error_catching():
    """Test that errors can be caught as their parent types."""

    def raise_database_not_found():
        raise DatabaseNotFoundError("Database not found")

    # Should be caught as DatabaseError
    with pytest.raises(DatabaseError):
        raise_database_not_found()

    # Should be caught as StorageError
    with pytest.raises(StorageError):
        raise_database_not_found()

    # Should be caught as DBMSError
    with pytest.raises(DBMSError):
        raise_database_not_found()

    # Should be caught as Exception
    with pytest.raises(Exception):
        raise_database_not_found()
