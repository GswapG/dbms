# Configuration

This page describes the global configuration system for the DBMS project. All major components (storage, executor, logging, client, etc.) use this system for their configurable settings.

## Overview

- **config.yaml** (project root): Optional YAML file where you can override default settings for the entire project.
- **config.py** (`src/common/config.py`): Python module that loads values from `config.yaml` if present, otherwise uses sensible defaults. All code should import config values from this module.

## Example config.yaml

```yaml
max_file_size_bytes: 104857600  # 100MB
batch_size: 1000
log_file: dbms_backend.log
type_sizes:
  VARCHAR: 255
  CHAR: 1
  INTEGER: 4
  BIGINT: 8
  FLOAT: 8
  DOUBLE: 8
  BOOLEAN: 1
  DATE: 8
  TIMESTAMP: 8
  FALLBACK: 16
```

## Current Config Options

| Key                 | Default Value         | Description                                 |
|---------------------|----------------------|---------------------------------------------|
| max_file_size_bytes | 104857600 (100MB)    | Max size for a single table data file       |
| batch_size          | 1000                 | Default batch size for reading rows         |
| log_file            | dbms_backend.log     | Log file name for all backend logs          |
| type_sizes          | see above            | Dict of type name to size in bytes          |

## Usage

- To override any setting, create or edit `config.yaml` in your project root.
- All code should import config values from `src/common/config.py`.
- This system ensures that all global constants are managed in one place and can be easily changed for different environments or builds.

## Extending

- Add new config options to both `config.py` and document them here.
- Reference this page from other documentation sections when mentioning configuration.
