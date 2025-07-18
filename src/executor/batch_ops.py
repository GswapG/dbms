from typing import Iterator, List, Dict, Any, Callable


def filter_batches(
    batches: Iterator[List[Dict[str, Any]]], predicate: Callable[[Dict[str, Any]], bool]
) -> Iterator[List[Dict[str, Any]]]:
    """
    Takes an iterator of batches, yields batches of filtered rows.
    """
    for batch in batches:
        filtered = [row for row in batch if predicate(row)]
        if filtered:
            yield filtered


def project_batches(
    batches: Iterator[List[Dict[str, Any]]], columns: List[str]
) -> Iterator[List[Dict[str, Any]]]:
    """
    Takes an iterator of batches, yields batches of projected rows.
    """
    for batch in batches:
        projected = [{col: row[col] for col in columns} for row in batch]
        if projected:
            yield projected
