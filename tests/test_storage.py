"""Tests for the storage engine component."""

import json
import os
from datetime import datetime
from pathlib import Path
import pytest
from typing import Generator

from dbms.storage import StorageEngine
from dbms.common.errors import DatabaseExistsError, StorageError, TableError


@pytest.fixture
def temp_db_dir(tmp_path) -> str:
    """Create a temporary database directory."""
    return str(tmp_path / "test_db")


@pytest.fixture
def storage_engine(temp_db_dir) -> StorageEngine:
    """Create a storage engine instance."""
    return StorageEngine(temp_db_dir)


def test_storage_engine_initialization(temp_db_dir: str) -> None:
    """Test storage engine initialization."""
    engine = StorageEngine(temp_db_dir)

    # Check that base directory was created
    assert Path(temp_db_dir).exists()
    assert Path(temp_db_dir).is_dir()

    # Check that global metadata file was created
    metadata_file = Path(temp_db_dir) / "global_metadata.json"
    assert metadata_file.exists()

    # Check metadata content
    with open(metadata_file) as f:
        metadata = json.load(f)
    assert metadata["version"] == "1.0"
    assert "created_at" in metadata
    assert "databases" in metadata
    assert isinstance(metadata["databases"], dict)


def test_create_database(storage_engine: StorageEngine, temp_db_dir: str) -> None:
    """Test database creation."""
    db_name = "test_db"
    uid = storage_engine.create_database(db_name)

    # Check that database directory was created
    db_dir = Path(temp_db_dir) / f"db_{uid}"
    assert db_dir.exists()
    assert db_dir.is_dir()

    # Check database metadata
    db_metadata_file = db_dir / "db_metadata.json"
    assert db_metadata_file.exists()
    with open(db_metadata_file) as f:
        db_metadata = json.load(f)
    assert db_metadata["version"] == "1.0"
    assert "created_at" in db_metadata
    assert "tables" in db_metadata
    assert "views" in db_metadata

    # Check global metadata
    assert db_name in storage_engine.metadata["databases"]
    assert storage_engine.metadata["databases"][db_name]["uid"] == uid


def test_create_duplicate_database(storage_engine: StorageEngine) -> None:
    """Test that creating a duplicate database raises an error."""
    db_name = "test_db"
    storage_engine.create_database(db_name)

    with pytest.raises(DatabaseExistsError) as exc_info:
        storage_engine.create_database(db_name)
    assert str(exc_info.value) == f"Database '{db_name}' already exists"


def test_invalid_metadata(temp_db_dir: str) -> None:
    """Test handling of invalid metadata file."""
    # Create invalid metadata file
    os.makedirs(temp_db_dir, exist_ok=True)
    with open(Path(temp_db_dir) / "global_metadata.json", "w") as f:
        f.write("invalid json")

    with pytest.raises(StorageError) as exc_info:
        StorageEngine(temp_db_dir)
    assert str(exc_info.value) == "Invalid global metadata format"


def test_create_table_with_columns_and_limits(
    storage_engine: StorageEngine, temp_db_dir: str
) -> None:
    """Test table creation with columns, max file size, and max rows per file."""
    db_name = "test_db"
    storage_engine.create_database(db_name)
    columns = [
        {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
        {"name": "username", "type": "VARCHAR(50)", "nullable": False},
        {"name": "email", "type": "VARCHAR(100)", "nullable": True},
        {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
    ]
    table_name = "users"
    uid = storage_engine.create_table(db_name, table_name, columns)

    # Check that table directory and metadata exist
    db_uid = storage_engine.metadata["databases"][db_name]["uid"]
    table_dir = Path(temp_db_dir) / f"db_{db_uid}" / f"table_{uid}"
    assert table_dir.exists()
    assert table_dir.is_dir()
    table_metadata_file = table_dir / "table_metadata.json"
    assert table_metadata_file.exists()
    with open(table_metadata_file) as f:
        table_metadata = json.load(f)
    assert table_metadata["columns"] == columns
    assert table_metadata["max_file_size_bytes"] == storage_engine.max_file_size_bytes
    # Calculate expected max row size
    expected_row_size = (
        4 + 50 + 100 + 8
    )  # INTEGER + VARCHAR(50) + VARCHAR(100) + TIMESTAMP
    expected_max_rows = storage_engine.max_file_size_bytes // expected_row_size
    assert table_metadata["max_rows_per_file"] == expected_max_rows
    # Check that data folder and first data file exist
    data_folder = table_dir / "data"
    assert data_folder.exists() and data_folder.is_dir()
    first_data_file = data_folder / "data_0.jsonl"
    assert first_data_file.exists()


def test_create_duplicate_table_raises(storage_engine: StorageEngine) -> None:
    """Test that creating a duplicate table raises an error."""
    db_name = "test_db"
    storage_engine.create_database(db_name)
    columns = [
        {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True}
    ]
    table_name = "users"
    storage_engine.create_table(db_name, table_name, columns)
    with pytest.raises(TableError) as exc_info:
        storage_engine.create_table(db_name, table_name, columns)
    assert f"Table '{table_name}' already exists" in str(exc_info.value)
