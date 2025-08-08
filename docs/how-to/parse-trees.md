# Parse Tree Visualization

This guide covers how to generate and interpret parse tree images for SQL queries.


## Enabling Parse Tree Generation

To generate parse tree images for SQL queries:

1. Set `generate_parse_tree_images = True` in your `src/common/config.py` or `config.yaml`.
2. (Optional) Set `PARSE_TREE_IMAGE_DIR` to control where images are saved.
3. Use the parser as usual; images will be generated automatically for each parse.

## Example

Parsing the following SQL:

```sql
SELECT name, age FROM users WHERE age > 30;
```

produces this parse tree image:

![Parse tree for SELECT ... WHERE ...](../images/parse_tree_select_where_example.png)

This tree shows the structure of the query, with nodes for SELECT, columns, FROM, WHERE, and the binary expression `age > 30`.

## Interpreting the Parse Tree

- Each node represents a grammar rule or token.
- Internal nodes correspond to non-terminals (e.g., `select_statement`, `expression`).
- Leaf nodes are tokens (e.g., `IDENTIFIER`, `NUMBER_LITERAL`).
- The tree structure helps debug and understand how the parser interprets SQL.

## Customizing and Debugging

- You can change the output directory for images using `PARSE_TREE_IMAGE_DIR`.
- Use parse trees to debug grammar issues or unexpected parses.

## See Also

- [Parser API Reference](../api/parser.md)
- [Parser Overview](../explanation/parser.md)
