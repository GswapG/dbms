"""Tests for the storage engine component."""

import json
import os
from datetime import datetime
from pathlib import Path
import pytest
from typing import Generator, List, Dict, Any

from dbms.storage import StorageEngine
from dbms.common.errors import DatabaseExistsError, StorageError, TableError


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
    first_data_file = data_folder / "data_0.csv"
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


def test_scan_table_and_append_rows(storage_engine: StorageEngine, temp_db_dir: str):
    db_name = "test_db"
    table_name = "users"
    columns = [
        {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
        {"name": "name", "type": "VARCHAR(20)", "nullable": False},
        {"name": "age", "type": "INTEGER", "nullable": False},
    ]
    storage_engine.create_database(db_name)
    storage_engine.create_table(db_name, table_name, columns)

    # Insert some rows
    rows = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35},
        {"id": 4, "name": "Diana", "age": 40},
        {"id": 5, "name": "Eve", "age": 22},
    ]
    storage_engine.append_rows(db_name, table_name, rows)

    # Scan in batches of 2
    batches = list(storage_engine.scan_table(db_name, table_name, batch_size=2))
    # Should yield 3 batches: [row1, row2], [row3, row4], [row5]
    assert len(batches) == 3
    flat = [row for batch in batches for row in batch]
    assert flat == rows

    # Append more rows and scan again
    more_rows = [
        {"id": 6, "name": "Frank", "age": 28},
        {"id": 7, "name": "Grace", "age": 31},
    ]
    storage_engine.append_rows(db_name, table_name, more_rows)
    all_rows = rows + more_rows
    batches = list(storage_engine.scan_table(db_name, table_name, batch_size=3))
    # Should yield 3 batches: [1,2,3], [4,5,6], [7]
    assert len(batches) == 3
    flat = [row for batch in batches for row in batch]
    assert flat == all_rows

    # Check that the latest_data_file in metadata is updated
    db_uid = storage_engine.metadata["databases"][db_name]["uid"]
    table_uid = storage_engine.metadata["databases"][db_name]["tables"][table_name][
        "uid"
    ]
    table_metadata_file = (
        Path(temp_db_dir)
        / f"db_{db_uid}"
        / f"table_{table_uid}"
        / "table_metadata.json"
    )
    with open(table_metadata_file) as f:
        table_metadata = json.load(f)
    assert table_metadata["latest_data_file"].startswith("data_")


def test_scan_sample_users_table(sample_users_table, storage_engine):
    db_name, table_name, columns, expected_rows = sample_users_table
    # Scan in batches of 20
    batches = list(storage_engine.scan_table(db_name, table_name, batch_size=20))
    # Should yield 5 batches of 20 rows each
    assert len(batches) == 5
    flat = [row for batch in batches for row in batch]
    # All ids should be unique and match expected
    assert sorted(row["id"] for row in flat) == sorted(
        row["id"] for row in expected_rows
    )
    assert len(flat) == 100


def collect_structure(root):
    structure = set()
    for path in Path(root).rglob("*"):
        rel = path.relative_to(root)
        # Normalize to forward slashes for comparison
        structure.add(str(rel).replace(os.sep, "/"))
    return structure


def test_integration_db_structure(sample_users_table, storage_engine, temp_db_dir):
    db_name, table_name, columns, expected_rows = sample_users_table
    db_uid = storage_engine.metadata["databases"][db_name]["uid"]
    table_uid = storage_engine.metadata["databases"][db_name]["tables"][table_name][
        "uid"
    ]
    expected = set(
        [
            f"global_metadata.json",
            f"db_{db_uid}",
            f"db_{db_uid}/db_metadata.json",
            f"db_{db_uid}/table_{table_uid}",
            f"db_{db_uid}/table_{table_uid}/table_metadata.json",
            f"db_{db_uid}/table_{table_uid}/data",
            f"db_{db_uid}/table_{table_uid}/data/data_0.csv",
        ]
    )
    # Normalize expected paths
    expected = set(p.replace(os.sep, "/") for p in expected)
    actual = collect_structure(temp_db_dir)
    for key in expected:
        assert key in actual, f"Missing: {key}"
    for key in actual:
        if not key.endswith(".gitkeep"):
            assert key in expected, f"Unexpected: {key}"
    data_file = (
        Path(temp_db_dir)
        / f"db_{db_uid}"
        / f"table_{table_uid}"
        / "data"
        / "data_0.csv"
    )
    with open(data_file, newline="") as f:
        import csv

        reader = csv.reader(f)
        header = next(reader)
        assert header == [col["name"] for col in columns]
