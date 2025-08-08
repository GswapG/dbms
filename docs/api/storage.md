# Storage Engine API Reference

## Configuration

See [Configuration](../explanation/configuration.md) for details on global settings (max file size, batch size, log file, type sizes, etc.).

---

## Main Class

### StorageEngine
The core class for all storage operations. Handles database and table creation, data storage, metadata management, and CRUD operations.

#### Methods

```python
def create_database(name: str) -> str
```
Create a new database.
- **name**: Name of the database
- **Returns**: Database UID

```python
def delete_database(db_name: str) -> None
```
Delete a database and all its tables and files. Updates global metadata.
- **db_name**: Name of the database

```python
def create_table(db_name: str, table_name: str, columns: List[Dict[str, Any]]) -> str
```
Create a new table in a database.
- **db_name**: Name of the database
- **table_name**: Name of the table
- **columns**: List of column definitions (dicts)
- **Returns**: Table UID

```python
def delete_table(db_name: str, table_name: str) -> None
```
Delete a table and all its files. Updates both global and db metadata.
- **db_name**: Name of the database
- **table_name**: Name of the table

```python
def append_rows(db_name: str, table_name: str, rows: List[Dict[str, Any]]) -> None
```
Append rows to a table, splitting files as needed. Handles CSV header logic.
- **db_name**: Name of the database
- **table_name**: Name of the table
- **rows**: List of row dictionaries

```python
def scan_table(db_name: str, table_name: str, batch_size: int = 1000) -> Iterator[List[Dict[str, Any]]]
```
Yield batches of rows from a table, converting types based on schema.
- **db_name**: Name of the database
- **table_name**: Name of the table
- **batch_size**: Number of rows per batch (default 1000)
- **Returns**: Iterator of row batches

## Metadata Files

- **global_metadata.json**: Tracks all databases.
- **db_metadata.json**: Tracks all tables in a database (now includes table names).
- **table_metadata.json**: Tracks schema and settings for a table (now includes table name).

## Logging
All operations are logged using the module-specific logger (`dbms.storage`) with automatic class name detection. Logs are written to `dbms_backend.log` by default.

```python
from dbms.common.logging_config import get_logger
logger = get_logger("storage")

# Class name "StorageEngine" is automatically detected in log messages
logger.info("Creating database: mydb")
```

## Example Usage
```python
engine = StorageEngine("/path/to/db_root")
engine.create_database("mydb")
engine.create_table("mydb", "users", columns=[...])
engine.append_rows("mydb", "users", [...])
for batch in engine.scan_table("mydb", "users", batch_size=100):
    ...
engine.delete_table("mydb", "users")
engine.delete_database("mydb")
```
