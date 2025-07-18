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

## Related Docs
- [Architecture Overview](./architecture.md)
- [Logging](./logging.md)
