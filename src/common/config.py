import os
import yaml
from typing import Dict, Any
import logging

# Default values
DEFAULT_MAX_FILE_SIZE_BYTES: int = 100 * 1024 * 1024  # 100MB
DEFAULT_BATCH_SIZE: int = 1000
DEFAULT_LOG_FILE: str = "dbms_backend.log"
DEFAULT_TYPE_SIZES: Dict[str, int] = {
    "VARCHAR": 255,  # fallback if not specified
    "CHAR": 1,  # fallback if not specified
    "INTEGER": 4,
    "BIGINT": 8,
    "FLOAT": 8,
    "DOUBLE": 8,
    "BOOLEAN": 1,
    "DATE": 8,
    "TIMESTAMP": 8,
    "FALLBACK": 16,  # unknown types
}

# Muted color palette for parse tree node types (can be overridden in config.yaml)
DEFAULT_PARSE_TREE_NODE_COLORS = {
    "SelectStatement": "#b3c6e7",
    "InsertStatement": "#b7e0c4",
    "UpdateStatement": "#f7e6a2",
    "DeleteStatement": "#f9d6b5",
    "FunctionCall": "#d6c1e6",
    "ColumnReference": "#b7e7e0",
    "Literal": "#f5c2d1",
    "CreateTableStatement": "#e0e0e0",
    "CreateDatabaseStatement": "#e0e0e0",
    "DropTableStatement": "#e0e0e0",
    "DropDatabaseStatement": "#e0e0e0",
    # Add more as needed
}
DEFAULT_PARSE_TREE_DEFAULT_NODE_COLOR = "#e0e0e0"

# Try to load from config.yaml in project root
CONFIG_PATH: str = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml"
)
config_data: Dict[str, Any] = {}
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        config_data = yaml.safe_load(f) or {}

MAX_FILE_SIZE_BYTES: int = int(
    config_data.get("max_file_size_bytes", DEFAULT_MAX_FILE_SIZE_BYTES)
)
BATCH_SIZE: int = int(config_data.get("batch_size", DEFAULT_BATCH_SIZE))
LOG_FILE: str = str(config_data.get("log_file", DEFAULT_LOG_FILE))
TYPE_SIZES: Dict[str, int] = dict(config_data.get("type_sizes", DEFAULT_TYPE_SIZES))

PARSE_TREE_IMAGE_DIR = "parse_trees"  # Default directory for parse tree images

# Add this config variable
generate_parse_tree_images = (
    True  # Set to True to enable parse tree image generation automatically
)

PARSE_TREE_NODE_COLORS = dict(
    config_data.get("parse_tree_node_colors", DEFAULT_PARSE_TREE_NODE_COLORS)
)
PARSE_TREE_DEFAULT_NODE_COLOR = str(
    config_data.get(
        "parse_tree_default_node_color", DEFAULT_PARSE_TREE_DEFAULT_NODE_COLOR
    )
)
