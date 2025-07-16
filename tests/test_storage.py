"""Tests for the storage engine component."""

import json
import os
from datetime import datetime
from pathlib import Path
import pytest
from typing import Generator

from dbms.storage import StorageEngine
from dbms.common.errors import DatabaseExistsError, StorageError


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
