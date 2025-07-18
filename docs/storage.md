# Storage Backend

This document describes how the DBMS stores data and metadata on disk.

## Directory Structure

Each database is stored in its own directory, with the following structure:

```text
<base_path>/
  db_<db_uid>/
    db_metadata.json         # Metadata for the database (tables, views, etc.)
    table_<table_uid>/
      table_metadata.json    # Metadata for the table (columns, file size, etc.)
      data/
        data_0.csv          # Data file (CSV format)
        data_1.csv          # Additional data files as needed
```

- All databases are stored under the configured `base_path`.
- Each database and table is assigned a unique UID.
- Table data is stored as CSV files, split into multiple files if the size exceeds the configured limit.

## Metadata File Structure

### Database Metadata (`db_metadata.json`)
```json
{
  "version": "1.0",
  "created_at": "...",
  "last_modified": "...",
  "tables": {
    "users": {
      "uid": "...",
      "created_at": "...",
      "last_modified": "..."
    }
  },
  "views": {}
}
```

### Table Metadata (`table_metadata.json`)
```json
{
  "version": "1.0",
  "created_at": "...",
  "last_modified": "...",
  "columns": [
    {"name": "id", "type": "INTEGER", "nullable": false, "primary_key": true},
    {"name": "username", "type": "VARCHAR(50)", "nullable": false}
  ],
  "max_file_size_bytes": 104857600,
  "max_rows_per_file": 123456
}
```

## Data Storage

- Table data is stored as CSV files in the `data/` subdirectory of each table.
- Each CSV file contains a subset of the table's rows, up to the configured size or row limit.
- New files are created as needed (e.g., `data_0.csv`, `data_1.csv`, ...).

## CSV File Structure

- **Every table's data is stored in one or more CSV files (e.g., `data_0.csv`, `data_1.csv`, ...).**
- **Each CSV file always starts with a header row** listing the column names, in the order defined by the table schema.
- **All subsequent rows are data rows** matching the schema.
- **When reading data, the system expects the header to be present and to match the schema.**
- **If the header is missing or malformed, reading will fail or produce incorrect results.**

**Example:**
```csv
id,name,age,email
1,Alice,30,alice@example.com
2,Bob,25,bob@example.com
... (more rows) ...
```

**Why is this important?**
- The header ensures that the mapping between column names and values is always correct.
- The storage engine uses the header to convert values to the correct types based on the schema.
- Appending and reading are robust and consistent as long as the header is always present.

## Related Docs
- [Architecture Overview](./architecture.md)
- [Logging](./logging.md)

## Configuration

See [Configuration](configuration.md) for details on global settings (max file size, batch size, log file, type sizes, etc.).

## Deleting Tables and Databases (DROP)

- **DROP TABLE:**
  - Use the `delete_table` method to remove a table from a database.
  - This operation deletes the table's directory and all its data files.
  - The table entry is removed from both the database metadata (`db_metadata.json`) and the global metadata (`global_metadata.json`).
  - All actions are logged for auditability.

- **DROP DATABASE:**
  - Use the `delete_database` method to remove an entire database.
  - This operation deletes the database directory and all its tables and data files.
  - The database entry is removed from the global metadata (`global_metadata.json`).
  - All actions are logged for auditability.

**Note:**
- These operations are thorough: all on-disk files and directories are removed, and all metadata is kept in sync.
- Attempting to delete a non-existent table or database will raise an error and log the failure.
