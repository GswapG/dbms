"""Global pytest fixtures and configuration."""

import os
import tempfile
import pytest
import csv
from dbms.storage import StorageEngine


@pytest.fixture
def temp_db_dir(tmp_path) -> str:
    """Create a temporary database directory."""
    return str(tmp_path / "test_db")


@pytest.fixture
def storage_engine(temp_db_dir) -> StorageEngine:
    """Create a storage engine instance."""
    return StorageEngine(temp_db_dir)


@pytest.fixture
def sample_users_table(storage_engine: StorageEngine, temp_db_dir: str):
    db_name = "test_db"
    table_name = "users"
    columns = [
        {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
        {"name": "name", "type": "VARCHAR(20)", "nullable": False},
        {"name": "age", "type": "INTEGER", "nullable": False},
        {"name": "email", "type": "VARCHAR(50)", "nullable": False},
    ]
    storage_engine.create_database(db_name)
    storage_engine.create_table(db_name, table_name, columns)
    # Load CSV data
    csv_path = os.path.join(os.path.dirname(__file__), "sample_data", "users.csv")
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(row) for row in reader]
        # Convert id and age to int
        for row in rows:
            row["id"] = int(row["id"])
            row["age"] = int(row["age"])
        storage_engine.append_rows(db_name, table_name, rows)
    return db_name, table_name, columns, rows


@pytest.fixture
def sample_orders_table(storage_engine: StorageEngine, temp_db_dir: str):
    db_name = "test_db"
    table_name = "orders"
    columns = [
        {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
        {"name": "user_id", "type": "INTEGER", "nullable": False},
        {"name": "amount", "type": "FLOAT", "nullable": False},
        {"name": "status", "type": "VARCHAR(20)", "nullable": False},
    ]
    storage_engine.create_table(db_name, table_name, columns)
    # Load CSV data
    csv_path = os.path.join(os.path.dirname(__file__), "sample_data", "orders.csv")
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(row) for row in reader]
        # Convert id, user_id to int, amount to float
        for row in rows:
            row["id"] = int(row["id"])
            row["user_id"] = int(row["user_id"])
            row["amount"] = float(row["amount"])
        storage_engine.append_rows(db_name, table_name, rows)
    return db_name, table_name, columns, rows
