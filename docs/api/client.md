# Client/Frontend API Reference

This page is a placeholder for future documentation of the client or frontend API.

---

## Main Classes and Methods (Template)

### ExampleClient
A sample client class for demonstration.

```python
class ExampleClient:
    def connect(self, host: str, port: int) -> None: ...
    def execute(self, query: str) -> dict: ...
```

#### Methods

```python
def connect(host: str, port: int) -> None
```
Connect to the database server.
- **host**: Hostname or IP address
- **port**: Port number

```python
def execute(query: str) -> dict
```
Execute a query and return the result.
- **query**: SQL query string
- **Returns**: Result as a dictionary

---

As client features (CLI, REST API, interactive shell, etc.) are implemented, document their main classes, methods, and usage here in this format.
