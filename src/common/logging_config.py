"""Centralized logging configuration for DBMS."""

import logging
import sys
from typing import Optional
from pathlib import Path

from .config import LOG_FILE


class ClassNameFormatter(logging.Formatter):
    """Custom formatter that automatically includes class names in log messages."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with automatic class name detection."""
        # Try to extract class name from the record
        class_name = self._extract_class_name(record)

        # Add class name to the record if found
        if class_name:
            record.class_name = class_name
            return super().format(record)
        else:
            # Fallback to original format without class name
            record.class_name = ""
            return super().format(record)

    def _extract_class_name(self, record: logging.LogRecord) -> Optional[str]:
        """Extract class name from the calling frame."""
        try:
            # Get the calling frame (the frame that called the logger)
            frame = record.funcName and getattr(record, "funcName", None)
            if not frame:
                return None

            # Look for 'self' in the calling frame's locals
            import inspect

            stack = inspect.stack()

            # Skip the first few frames (logging internals)
            for frame_info in stack[3:]:  # Skip logging internals
                frame_locals = frame_info.frame.f_locals

                # Check if 'self' exists and has a __class__ attribute
                if "self" in frame_locals:
                    self_obj = frame_locals["self"]
                    if hasattr(self_obj, "__class__"):
                        class_name = self_obj.__class__.__name__
                        if isinstance(class_name, str):
                            return class_name

                # Also check for 'cls' (class methods)
                if "cls" in frame_locals:
                    cls_obj = frame_locals["cls"]
                    if hasattr(cls_obj, "__name__"):
                        class_name = cls_obj.__name__
                        if isinstance(class_name, str):
                            return class_name

            return None
        except Exception:
            # If anything goes wrong, return None
            return None


def setup_logging(
    log_file: Optional[str] = None,
    log_level: int = logging.INFO,
    enable_console: bool = False,
) -> None:
    """Set up centralized logging configuration.

    Args:
        log_file: Path to log file (defaults to config LOG_FILE)
        log_level: Logging level (defaults to INFO)
        enable_console: Whether to also log to console
    """
    log_file = log_file or LOG_FILE

    # Create formatter with automatic class name detection
    formatter = ClassNameFormatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(class_name)s.%(funcName)s] %(message)s"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler (optional)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Set specific loggers for each module
    _setup_module_loggers()


def _setup_module_loggers() -> None:
    """Set up specific loggers for each major module."""

    # Storage module logger
    storage_logger = logging.getLogger("dbms.storage")
    storage_logger.setLevel(logging.DEBUG)

    # Parser module logger
    parser_logger = logging.getLogger("dbms.parser")
    parser_logger.setLevel(logging.DEBUG)

    # Executor module logger
    executor_logger = logging.getLogger("dbms.executor")
    executor_logger.setLevel(logging.DEBUG)

    # Client module logger
    client_logger = logging.getLogger("dbms.client")
    client_logger.setLevel(logging.DEBUG)

    # Common module logger
    common_logger = logging.getLogger("dbms.common")
    common_logger.setLevel(logging.DEBUG)


def get_logger(module_name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        module_name: Name of the module (e.g., 'storage', 'parser', 'executor')

    Returns:
        Configured logger for the module
    """
    return logging.getLogger(f"dbms.{module_name}")


# Initialize logging when module is imported
setup_logging()
