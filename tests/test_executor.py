import pytest
from dbms.executor.batch_ops import filter_batches, project_batches
from dbms.executor.executor import Executor
from dbms.executor.sinks import OutputSink, InsertSink, TempTupleSink, BaseSink
from typing import List, Dict, Any, Iterator

# Sample data for testing
batches = [
    [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35},
    ],
    [
        {"id": 4, "name": "Diana", "age": 40},
        {"id": 5, "name": "Eve", "age": 22},
    ],
]


def test_filter_batches():
    # Filter: age > 30
    filtered = list(filter_batches(iter(batches), lambda row: row["age"] > 30))
    # Should only include Charlie (35) and Diana (40)
    expected = [
        [{"id": 3, "name": "Charlie", "age": 35}],
        [{"id": 4, "name": "Diana", "age": 40}],
    ]
    # Flatten for easier comparison
    flat_filtered = [row for batch in filtered for row in batch]
    flat_expected = [row for batch in expected for row in batch]
    assert flat_filtered == flat_expected


def test_project_batches():
    # Project: only 'name' and 'age'
    projected = list(project_batches(iter(batches), ["name", "age"]))
    expected = [
        [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ],
        [
            {"name": "Diana", "age": 40},
            {"name": "Eve", "age": 22},
        ],
    ]
    assert projected == expected


def test_filter_and_project_pipeline():
    # Filter: age >= 30, then project 'name'
    filtered = filter_batches(iter(batches), lambda row: row["age"] >= 30)
    projected = list(project_batches(filtered, ["name"]))
    expected = [
        [{"name": "Alice"}, {"name": "Charlie"}],
        [{"name": "Diana"}],
    ]
    assert projected == expected


def test_output_sink():
    sink = OutputSink()
    sink.consume(iter(batches))
    expected = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35},
        {"id": 4, "name": "Diana", "age": 40},
        {"id": 5, "name": "Eve", "age": 22},
    ]
    assert sink.get_results() == expected


def test_temp_tuple_sink():
    sink = TempTupleSink(["id", "name"])
    sink.consume(iter(batches))
    expected = [
        (1, "Alice"),
        (2, "Bob"),
        (3, "Charlie"),
        (4, "Diana"),
        (5, "Eve"),
    ]
    assert sink.get_results() == expected


def test_executor_pipeline_with_output_sink(monkeypatch):
    # Mock StorageEngine.scan_table to yield our sample batches
    class DummyStorage:
        def scan_table(self, db, table, batch_size):
            return iter(batches)

    executor = Executor(DummyStorage())
    sink = OutputSink()
    executor.run_pipeline(
        db_name="db",
        table_name="t",
        batch_size=2,
        predicate=lambda row: row["age"] > 30,
        columns=["name"],
        sink=sink,
    )
    # Only Charlie and Diana, projected to name
    assert sink.get_results() == [{"name": "Charlie"}, {"name": "Diana"}]


def test_executor_pipeline_with_temp_tuple_sink(monkeypatch):
    class DummyStorage:
        def scan_table(self, db, table, batch_size):
            return iter(batches)

    executor = Executor(DummyStorage())
    sink = TempTupleSink(["id", "age"])
    executor.run_pipeline(
        db_name="db",
        table_name="t",
        batch_size=2,
        predicate=lambda row: row["age"] >= 30,
        columns=["id", "age"],
        sink=sink,
    )
    # Alice, Charlie, Diana
    assert sink.get_results() == [(1, 30), (3, 35), (4, 40)]


def test_insert_sink_calls_append_rows(monkeypatch):
    # Track calls to append_rows
    called_batches = []

    class DummyStorage:
        def scan_table(self, db, table, batch_size):
            return iter(batches)

        def append_rows(self, db, table, batch):
            called_batches.append(batch)

    executor = Executor(DummyStorage())
    sink = InsertSink(DummyStorage(), "db", "t")
    executor.run_pipeline(
        db_name="db",
        table_name="t",
        batch_size=2,
        predicate=None,
        columns=None,
        sink=sink,
    )
    # Should call append_rows for each batch
    assert called_batches == batches
