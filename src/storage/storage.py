"""Storage engine implementation."""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List

from ..common.errors import (
    StorageError,
    DatabaseError,
    DatabaseExistsError,
    TableError,
)


def generate_uid() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


class StorageEngine:
    """Storage engine implementation."""

    def __init__(self, base_path: str) -> None:
        """Initialize storage engine.

        Args:
            base_path: Path to the database directory
        """
        self.base_path = Path(base_path)
        self.metadata: Dict[str, Any] = {}
        self._ensure_base_structure()
        self._load_global_metadata()

    def _ensure_base_structure(self) -> None:
        """Ensure base directory structure exists."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        metadata_file = self.base_path / "global_metadata.json"
        if not metadata_file.exists():
            initial_metadata = {
                "version": "1.0",
                "created_at": datetime.utcnow().isoformat(),
                "databases": {},  # name -> {uid, created_at, last_modified}
            }
            with open(metadata_file, "w") as f:
                json.dump(initial_metadata, f, indent=2)

    def _load_global_metadata(self) -> None:
        """Load global metadata from file."""
        try:
            with open(self.base_path / "global_metadata.json", "r") as f:
                self.metadata = json.load(f)
        except FileNotFoundError:
            raise StorageError("Global metadata file not found")
        except json.JSONDecodeError:
            raise StorageError("Invalid global metadata format")

    def _save_global_metadata(self) -> None:
        """Save global metadata to file."""
        self.metadata["last_modified"] = datetime.utcnow().isoformat()
        with open(self.base_path / "global_metadata.json", "w") as f:
            json.dump(self.metadata, f, indent=2)

    def create_database(self, name: str) -> str:
        """Create a new database.

        Args:
            name: Database name

        Returns:
            Database UID

        Raises:
            DatabaseError: If database with same name exists
        """
        if name in self.metadata["databases"]:
            raise DatabaseExistsError(f"Database '{name}' already exists")

        # Generate UID and create directory
        uid = generate_uid()
        db_path = self.base_path / f"db_{uid}"
        db_path.mkdir()

        # Create database metadata
        timestamp = datetime.utcnow().isoformat()
        db_metadata = {
            "version": "1.0",
            "created_at": timestamp,
            "last_modified": timestamp,
            "tables": {},  # name -> {uid, created_at, last_modified}
            "views": {},
        }
        with open(db_path / "db_metadata.json", "w") as f:
            json.dump(db_metadata, f, indent=2)

        # Update global metadata
        self.metadata["databases"][name] = {
            "uid": uid,
            "created_at": timestamp,
            "last_modified": timestamp,
        }
        self._save_global_metadata()

        return uid
