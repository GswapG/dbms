import os
import yaml
from typing import Dict, Any

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
