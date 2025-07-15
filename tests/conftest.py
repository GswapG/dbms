"""
Global pytest fixtures and configuration.
"""
import pytest
import os
import tempfile

@pytest.fixture
def temp_db_file():
    """Fixture to create a temporary database file."""
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.unlink(path)

@pytest.fixture
def setup_test_db():
    """Fixture to set up a test database with some initial data."""
    # This will be implemented once we have our storage engine
    pass
