from typing import Iterator, List, Dict, Any, Callable, Optional
from ..storage.storage import StorageEngine
from .batch_ops import filter_batches, project_batches
from .sinks import BaseSink, OutputSink, InsertSink


class Executor:
    def __init__(self, storage_engine: StorageEngine):
        self.storage_engine = storage_engine
        # In the future, you can add a registry of query handlers here

    def run_pipeline(
        self,
        db_name: str,
        table_name: str,
        batch_size: int,
        predicate: Optional[Callable[[Dict[str, Any]], bool]],
        columns: Optional[List[str]],
        sink: BaseSink,
    ) -> None:
        # This is a simple SELECT pipeline handler.
        # For other query types (INSERT, UPDATE, etc.), add handler methods.
        batches = self.storage_engine.scan_table(db_name, table_name, batch_size)
        if predicate:
            batches = filter_batches(batches, predicate)
        if columns:
            batches = project_batches(batches, columns)
        sink.consume(batches)
