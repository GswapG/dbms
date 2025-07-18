"""Storage engine implementation."""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Any, List, Iterator
import logging
import csv

from ..common.errors import (
    StorageError,
    DatabaseError,
    DatabaseExistsError,
    TableError,
)


def generate_uid() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


# Configure global logger
logger = logging.getLogger("dbms")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("dbms_backend.log")
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s] %(message)s"
)
file_handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(file_handler)


class StorageEngine:
    """Storage engine implementation."""

    DEFAULT_MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100MB

    def __init__(
        self, base_path: str, max_file_size_bytes: Optional[int] = None
    ) -> None:
        """Initialize storage engine.

        Args:
            base_path: Path to the databases directory
            max_file_size_bytes: Max file size for table data files (in bytes)
        """
        logger.info(f"[StorageEngine] Initializing with base_path: {base_path}")
        self.base_path = Path(base_path)
        self.metadata: Dict[str, Any] = {}
        self.max_file_size_bytes = (
            max_file_size_bytes or self.DEFAULT_MAX_FILE_SIZE_BYTES
        )
        self._ensure_base_structure()
        self._load_global_metadata()
        logger.info(f"[StorageEngine] Initialization complete.")

    def _ensure_base_structure(self) -> None:
        """Ensure base directory structure exists."""
        logger.debug(
            f"[StorageEngine] Ensuring base directory structure at {self.base_path}"
        )
        self.base_path.mkdir(parents=True, exist_ok=True)
        metadata_file = self.base_path / "global_metadata.json"
        if not metadata_file.exists():
            logger.info(
                f"[StorageEngine] Creating new global metadata file at {metadata_file}"
            )
            initial_metadata = {
                "version": "1.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "databases": {},  # name -> {uid, created_at, last_modified}
            }
            with open(metadata_file, "w") as f:
                json.dump(initial_metadata, f, indent=2)
        else:
            logger.debug(
                f"[StorageEngine] Global metadata file already exists at {metadata_file}"
            )

    def _load_global_metadata(self) -> None:
        """Load global metadata from file."""
        logger.debug(
            f"[StorageEngine] Loading global metadata from {self.base_path / 'global_metadata.json'}"
        )
        try:
            with open(self.base_path / "global_metadata.json", "r") as f:
                self.metadata = json.load(f)
            logger.info(f"[StorageEngine] Global metadata loaded successfully.")
        except FileNotFoundError:
            logger.error(f"[StorageEngine] Global metadata file not found.")
            raise StorageError("Global metadata file not found")
        except json.JSONDecodeError:
            logger.error(f"[StorageEngine] Invalid global metadata format.")
            raise StorageError("Invalid global metadata format")

    def _save_global_metadata(self) -> None:
        """Save global metadata to file."""
        logger.debug(
            f"[StorageEngine] Saving global metadata to {self.base_path / 'global_metadata.json'}"
        )
        self.metadata["last_modified"] = datetime.now(timezone.utc).isoformat()
        with open(self.base_path / "global_metadata.json", "w") as f:
            json.dump(self.metadata, f, indent=2)
        logger.info(f"[StorageEngine] Global metadata saved.")

    def create_database(self, name: str) -> str:
        """Create a new database.

        Args:
            name: Database name

        Returns:
            Database UID

        Raises:
            DatabaseError: If database with same name exists
        """
        logger.info(f"[StorageEngine] Creating database: {name}")
        if name in self.metadata["databases"]:
            logger.warning(f"[StorageEngine] Database '{name}' already exists.")
            raise DatabaseExistsError(f"Database '{name}' already exists")

        # Generate UID and create directory
        uid = generate_uid()
        db_path = self.base_path / f"db_{uid}"
        db_path.mkdir()
        logger.info(
            f"[StorageEngine] Created directory for database '{name}' at {db_path}"
        )

        # Create database metadata
        timestamp = datetime.now(timezone.utc).isoformat()
        db_metadata = {
            "version": "1.0",
            "name": name,
            "created_at": timestamp,
            "last_modified": timestamp,
            "tables": {},  # name -> {uid, created_at, last_modified}
            "views": {},
        }
        with open(db_path / "db_metadata.json", "w") as f:
            json.dump(db_metadata, f, indent=2)
        logger.debug(f"[StorageEngine] Created db_metadata.json for '{name}'")

        # Update global metadata
        self.metadata["databases"][name] = {
            "uid": uid,
            "created_at": timestamp,
            "last_modified": timestamp,
            "tables": {},
        }
        self._save_global_metadata()
        logger.info(f"[StorageEngine] Database '{name}' created with UID {uid}")
        return uid

    def create_table(
        self, db_name: str, table_name: str, columns: List[Dict[str, Any]]
    ) -> str:
        """Create a new table.

        Args:
            db_name: Database name
            table_name: Table name
            columns: List of column definitions (dicts)

        Returns:
            Table UID
        """
        logger.info(
            f"[StorageEngine] Creating table: {table_name} in database: {db_name} with columns: {columns}"
        )
        if db_name not in self.metadata["databases"]:
            logger.error(f"[StorageEngine] Database '{db_name}' not found.")
            raise DatabaseError(f"Database '{db_name}' not found")
        # Ensure 'tables' key exists in in-memory metadata
        if "tables" not in self.metadata["databases"][db_name]:
            self.metadata["databases"][db_name]["tables"] = {}
        if table_name in self.metadata["databases"][db_name]["tables"]:
            logger.error(
                f"[StorageEngine] Table '{table_name}' already exists in database '{db_name}'."
            )
            raise TableError(
                f"Table '{table_name}' already exists in database '{db_name}'"
            )

        # Generate UID and create directory
        uid = generate_uid()
        db_uid = self.metadata["databases"][db_name]["uid"]
        table_path = self.base_path / f"db_{db_uid}" / f"table_{uid}"
        table_path.mkdir()

        # Calculate max row size
        def get_col_size(col: Dict[str, Any]) -> int:
            t = col["type"].upper()
            if t.startswith("VARCHAR"):
                import re

                m = re.match(r"VARCHAR\((\d+)\)", t)
                return int(m.group(1)) if m else 255
            if t.startswith("CHAR"):
                import re

                m = re.match(r"CHAR\((\d+)\)", t)
                return int(m.group(1)) if m else 1
            if t == "INTEGER":
                return 4
            if t == "BIGINT":
                return 8
            if t in ("FLOAT", "DOUBLE"):
                return 8
            if t == "BOOLEAN":
                return 1
            if t in ("DATE", "TIMESTAMP"):
                return 8
            return 16  # fallback for unknown types

        max_row_size = sum(get_col_size(col) for col in columns)
        max_file_size_bytes = self.max_file_size_bytes
        max_rows_per_file = (
            max_file_size_bytes // max_row_size if max_row_size > 0 else 0
        )

        # Create table metadata
        timestamp = datetime.now(timezone.utc).isoformat()
        table_metadata = {
            "version": "1.0",
            "name": table_name,
            "created_at": timestamp,
            "last_modified": timestamp,
            "columns": columns,
            "max_file_size_bytes": max_file_size_bytes,
            "max_rows_per_file": max_rows_per_file,
            "latest_data_file": "data_0.csv",
        }
        with open(table_path / "table_metadata.json", "w") as f:
            json.dump(table_metadata, f, indent=2)
        logger.info(
            f"[StorageEngine] Table metadata for '{table_name}': {table_metadata}"
        )

        # Create folder for data files and the first data file
        data_folder = table_path / "data"
        data_folder.mkdir()
        first_data_file = data_folder / "data_0.csv"

        with open(first_data_file, "w", newline="") as f:
            pass  # create empty file
        logger.info(
            f"[StorageEngine] Created first data file for '{table_name}' at {first_data_file}"
        )

        # Update global metadata
        self.metadata["databases"][db_name]["tables"][table_name] = {
            "uid": uid,
            "created_at": timestamp,
            "last_modified": timestamp,
        }
        self._save_global_metadata()

        # Update db_metadata.json to include the new table
        db_metadata_file = self.base_path / f"db_{db_uid}" / "db_metadata.json"
        with open(db_metadata_file, "r") as f:
            db_metadata = json.load(f)
        db_metadata["tables"][table_name] = {
            "uid": uid,
            "name": table_name,
            "created_at": timestamp,
            "last_modified": timestamp,
        }
        with open(db_metadata_file, "w") as f:
            json.dump(db_metadata, f, indent=2)

        logger.info(f"[StorageEngine] Table '{table_name}' created with UID {uid}")
        return uid

    def scan_table(
        self, db_name: str, table_name: str, batch_size: int = 1000
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Yield batches of rows from the specified table as lists of dictionaries.
        Converts values to correct types based on table metadata.
        """
        db_uid = self.metadata["databases"][db_name]["uid"]
        table_uid = self.metadata["databases"][db_name]["tables"][table_name]["uid"]
        table_dir = self.base_path / f"db_{db_uid}" / f"table_{table_uid}"
        data_dir = table_dir / "data"
        table_metadata_file = table_dir / "table_metadata.json"
        import json

        with open(table_metadata_file) as f:
            table_metadata = json.load(f)
        col_types = {
            col["name"]: col["type"].upper() for col in table_metadata["columns"]
        }

        def convert_value(val: Any, typ: str) -> Any:
            if val == "" or val is None:
                return None
            if typ.startswith("VARCHAR") or typ.startswith("CHAR"):
                return str(val)
            if typ == "INTEGER":
                return int(val)
            if typ == "BIGINT":
                return int(val)
            if typ in ("FLOAT", "DOUBLE"):
                return float(val)
            if typ == "BOOLEAN":
                return val.lower() in ("1", "true", "yes")
            if typ in ("DATE", "TIMESTAMP"):
                return str(val)  # Could parse to datetime if needed
            return val

        batch = []
        for data_file in sorted(os.listdir(data_dir)):
            if not data_file.endswith(".csv"):
                continue
            with open(data_dir / data_file, newline="") as f:
                import csv

                reader = csv.DictReader(f)
                for row in reader:
                    print("row type: ", type(row))
                    print("row: ", row)
                    typed_row = {
                        col: convert_value(row[col], col_types[col]) for col in row
                    }
                    batch.append(typed_row)
                    if len(batch) == batch_size:
                        yield batch
                        batch = []
        if batch:
            yield batch

    def append_rows(
        self, db_name: str, table_name: str, rows: List[Dict[str, Any]]
    ) -> None:
        """
        Append rows to the table's latest CSV file, or create a new file if needed. Updates table metadata to track the latest data file.
        """
        import csv, json

        db_uid = self.metadata["databases"][db_name]["uid"]
        table_uid = self.metadata["databases"][db_name]["tables"][table_name]["uid"]
        table_dir = self.base_path / f"db_{db_uid}" / f"table_{table_uid}"
        data_dir = table_dir / "data"
        table_metadata_file = table_dir / "table_metadata.json"
        with open(table_metadata_file) as f:
            table_metadata = json.load(f)
        max_rows = table_metadata["max_rows_per_file"]
        columns = [col["name"] for col in table_metadata["columns"]]
        # Optimization: track latest data file in metadata
        latest_file = table_metadata.get("latest_data_file", "data_0.csv")
        file_path = data_dir / latest_file
        # Count current rows in latest file
        current_rows = 0
        if file_path.exists():
            with open(file_path, newline="") as f:
                current_rows = sum(1 for _ in f) - 1  # minus header
        to_write = rows[:]
        file_idx = int(latest_file.split("_")[1].split(".")[0])
        while to_write:
            space_left = max_rows - current_rows
            batch = to_write[:space_left]
            to_write = to_write[space_left:]
            write_header = (
                not file_path.exists() or current_rows <= 0
            )  # might be -1 if no header (first inser  t)
            with open(file_path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                if write_header:
                    writer.writeheader()
                writer.writerows(batch)
            if to_write:
                file_idx += 1
                file_path = data_dir / f"data_{file_idx}.csv"
                current_rows = 0
            else:
                current_rows += len(batch)
        # Update latest_data_file in table metadata
        table_metadata["latest_data_file"] = f"data_{file_idx}.csv"
        with open(table_metadata_file, "w") as f:
            json.dump(table_metadata, f, indent=2)
