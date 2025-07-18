from typing import Iterator, List, Dict, Any
from ..storage.storage import StorageEngine


class BaseSink:
    def consume(self, batches: Iterator[List[Dict[str, Any]]]) -> None:
        raise NotImplementedError


class OutputSink(BaseSink):
    def __init__(self) -> None:
        self.results: List[Dict[str, Any]] = []

    def consume(self, batches: Iterator[List[Dict[str, Any]]]) -> None:
        for batch in batches:
            self.results.extend(batch)

    def get_results(self) -> List[Dict[str, Any]]:
        return self.results


class InsertSink(BaseSink):
    def __init__(
        self, storage_engine: StorageEngine, db_name: str, table_name: str
    ) -> None:
        self.storage_engine = storage_engine
        self.db_name = db_name
        self.table_name = table_name

    def consume(self, batches: Iterator[List[Dict[str, Any]]]) -> None:
        for batch in batches:
            self.storage_engine.append_rows(self.db_name, self.table_name, batch)


class TempTupleSink(BaseSink):
    """A sink for testing: collects results as a list of tuples (one tuple per row, columns in order)."""

    def __init__(self, columns: List[str]) -> None:
        self.columns = columns
        self.results: List[tuple[Any, ...]] = []

    def consume(self, batches: Iterator[List[Dict[str, Any]]]) -> None:
        for batch in batches:
            for row in batch:
                self.results.append(tuple(row[col] for col in self.columns))

    def get_results(self) -> List[tuple[Any, ...]]:
        return self.results
