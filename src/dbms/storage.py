"""Storage engine implementation."""

from typing import Optional, BinaryIO


class StorageEngine:
    """Base class for storage engine implementation."""

    def __init__(self, path: str) -> None:
        """Initialize storage engine.

        Args:
            path: Path to the database file
        """
        self.path = path
        self._file: Optional[BinaryIO] = None

    def open(self) -> None:
        """Open the database file."""
        if self._file is None:
            self._file = open(self.path, "ab+")

    def close(self) -> None:
        """Close the database file."""
        if self._file is not None:
            self._file.close()
            self._file = None
