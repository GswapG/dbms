"""Tests for the new logging system."""

import pytest
import logging
import tempfile
import os
from pathlib import Path

from dbms.common.logging_config import setup_logging, get_logger, ClassNameFormatter


class TestClass:
    """Test class to verify automatic class name detection."""

    def __init__(self):
        self.logger = get_logger("test")

    def test_method(self):
        """Test method that logs a message."""
        self.logger.info("This is a test message from TestClass")

    @classmethod
    def test_class_method(cls):
        """Test class method that logs a message."""
        logger = get_logger("test")
        logger.info("This is a test message from TestClass class method")


def test_logging_setup():
    """Test that logging setup works correctly."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        log_file = tmp.name

    try:
        # Setup logging with test file
        setup_logging(log_file=log_file, log_level=logging.DEBUG)

        # Get loggers for different modules
        storage_logger = get_logger("storage")
        parser_logger = get_logger("parser")
        executor_logger = get_logger("executor")
        client_logger = get_logger("client")

        # Verify logger names
        assert storage_logger.name == "dbms.storage"
        assert parser_logger.name == "dbms.parser"
        assert executor_logger.name == "dbms.executor"
        assert client_logger.name == "dbms.client"

        # Test logging messages
        storage_logger.info("Storage test message")
        parser_logger.info("Parser test message")
        executor_logger.info("Executor test message")
        client_logger.info("Client test message")

        # Verify log file was created and contains messages
        assert os.path.exists(log_file)

        with open(log_file, "r") as f:
            log_content = f.read()

        assert "Storage test message" in log_content
        assert "Parser test message" in log_content
        assert "Executor test message" in log_content
        assert "Client test message" in log_content

    finally:
        # Cleanup - close all handlers first
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)

        # Wait a bit for file handles to be released
        import time

        time.sleep(0.1)

        # Now try to delete the file
        try:
            if os.path.exists(log_file):
                os.unlink(log_file)
        except PermissionError:
            # If we can't delete it, that's okay for the test
            pass


def test_class_name_detection():
    """Test that class names are automatically detected in log messages."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        log_file = tmp.name

    try:
        # Setup logging
        setup_logging(log_file=log_file, log_level=logging.DEBUG)

        # Create test instance and log messages
        test_instance = TestClass()
        test_instance.test_method()
        TestClass.test_class_method()

        # Verify log file contains class names
        with open(log_file, "r") as f:
            log_content = f.read()

        # Check that class name appears in log messages
        assert "TestClass" in log_content
        assert "This is a test message from TestClass" in log_content

    finally:
        # Cleanup - close all handlers first
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)

        # Wait a bit for file handles to be released
        import time

        time.sleep(0.1)

        # Now try to delete the file
        try:
            if os.path.exists(log_file):
                os.unlink(log_file)
        except PermissionError:
            # If we can't delete it, that's okay for the test
            pass


def test_formatter_class_name_extraction():
    """Test the ClassNameFormatter's class name extraction logic."""
    formatter = ClassNameFormatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(class_name)s.%(funcName)s] %(message)s"
    )

    # Create a mock log record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    record.funcName = "test_method"

    # Test formatting (should handle missing class name gracefully)
    formatted = formatter.format(record)
    assert "Test message" in formatted
    assert "test_method" in formatted


def test_module_specific_loggers():
    """Test that each module gets its own logger with correct configuration."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        log_file = tmp.name

    try:
        setup_logging(log_file=log_file, log_level=logging.DEBUG)

        # Test each module logger
        modules = ["storage", "parser", "executor", "client", "common"]

        for module in modules:
            logger = get_logger(module)

            # Verify logger name format
            assert logger.name == f"dbms.{module}"

            # Verify logger level is set to DEBUG
            assert logger.level == logging.DEBUG

            # Test logging a message
            logger.info(f"Test message from {module} module")

        # Verify all messages are in log file
        with open(log_file, "r") as f:
            log_content = f.read()

        for module in modules:
            assert f"Test message from {module} module" in log_content
            assert f"dbms.{module}" in log_content

    finally:
        # Cleanup - close all handlers first
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)

        # Wait a bit for file handles to be released
        import time

        time.sleep(0.1)

        # Now try to delete the file
        try:
            if os.path.exists(log_file):
                os.unlink(log_file)
        except PermissionError:
            # If we can't delete it, that's okay for the test
            pass
