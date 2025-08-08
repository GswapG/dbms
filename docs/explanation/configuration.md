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


| Key                        | Default Value                | Description                                              |
|----------------------------|------------------------------|----------------------------------------------------------|
| max_file_size_bytes        | 104857600 (100MB)            | Max size for a single table data file                    |
| batch_size                 | 1000                         | Default batch size for reading rows                      |
| log_file                   | dbms_backend.log             | Log file name for all backend logs                       |
| type_sizes                 | see above                    | Dict of type name to size in bytes                       |
| generate_parse_tree_images | False                        | Enable/disable parse tree image generation (parser)       |
| PARSE_TREE_IMAGE_DIR       | parse_trees                  | Directory for generated parse tree images                 |
| parse_tree_image_format    | png                          | Image format for parse tree images                        |
| parser_debug               | False                        | Enable verbose parser debug output                        |
| parser_max_errors          | 10                           | Max errors before parser aborts                           |
| parser_error_context_lines | 2                            | Lines of context to show in error messages                |


## Usage

- To override any setting, create or edit `config.yaml` in your project root.
- All code should import config values from `src/common/config.py`.
- This system ensures that all global constants are managed in one place and can be easily changed for different environments or builds.

## Parser-Specific Configuration

- `generate_parse_tree_images`: Set to `True` to enable parse tree image generation for every parsed SQL statement.
- `PARSE_TREE_IMAGE_DIR`: Directory where parse tree images are saved. Default is `parse_trees`.
- `parse_tree_image_format`: Image format for parse tree images (e.g., `png`).
- `parser_debug`: Enable verbose debug output from the parser.
- `parser_max_errors`: Maximum number of errors before the parser aborts.
- `parser_error_context_lines`: Number of lines of context to show in error messages.

These options can be set in `config.yaml` or directly in `src/common/config.py`.

## Extending

- Add new config options to both `config.py` and document them here.
- Reference this page from other documentation sections when mentioning configuration.
