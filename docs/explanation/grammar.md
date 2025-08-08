# SQL Parser Grammar Reference

---

## Overview

This document provides a detailed reference for the SQL grammar implemented in the DBMS parser. The grammar is defined using PLY (Python Lex-Yacc) and follows standard SQL syntax conventions.

## Grammar Notation

- **UPPERCASE**: Terminal tokens (keywords, operators, literals)
- **lowercase**: Non-terminal symbols (grammar rules)
- **|**: Alternative productions
- **[]**: Optional elements
- **{}**: Zero or more repetitions
- **()**: Grouping

## Complete Grammar

### Top-Level Productions

```
statement : sql_statement SEMICOLON
         | sql_statement

sql_statement : select_statement
             | insert_statement
             | update_statement
             | delete_statement
             | create_statement
             | drop_statement
```

### SELECT Statement Grammar

```
select_statement : SELECT DISTINCT column_list FROM table_reference where_clause_opt group_by_opt having_opt order_by_opt limit_opt
                | SELECT column_list FROM table_reference where_clause_opt group_by_opt having_opt order_by_opt limit_opt

column_list : ASTERISK
           | column_expression_list

column_expression_list : column_expression
                      | column_expression_list COMMA column_expression

column_expression : column_reference
                 | function_call
                 | STRING_LITERAL
                 | NUMBER_LITERAL
                 | BOOLEAN_LITERAL

table_reference : IDENTIFIER
               | IDENTIFIER AS IDENTIFIER
               | IDENTIFIER IDENTIFIER

where_clause_opt : WHERE expression
                | empty

group_by_opt : GROUP BY column_reference_list
            | empty

having_opt : HAVING expression
          | empty

order_by_opt : ORDER BY order_item_list
            | empty

limit_opt : LIMIT NUMBER_LITERAL
         | LIMIT NUMBER_LITERAL OFFSET NUMBER_LITERAL
         | empty
```

### INSERT Statement Grammar

```
insert_statement : INSERT INTO IDENTIFIER column_list_opt VALUES values_list

column_list_opt : LEFT_PAREN identifier_list RIGHT_PAREN
               | empty

identifier_list : IDENTIFIER
               | identifier_list COMMA IDENTIFIER

values_list : LEFT_PAREN value_list RIGHT_PAREN
           | values_list COMMA LEFT_PAREN value_list RIGHT_PAREN

value_list : expression
          | value_list COMMA expression
```

### UPDATE Statement Grammar

```
update_statement : UPDATE IDENTIFIER SET set_clause where_clause_opt

set_clause : IDENTIFIER EQUALS expression
          | set_clause COMMA IDENTIFIER EQUALS expression
```

### DELETE Statement Grammar

```
delete_statement : DELETE FROM IDENTIFIER where_clause_opt
```

### CREATE Statement Grammar

```
create_statement : CREATE TABLE IDENTIFIER LEFT_PAREN column_definition_list RIGHT_PAREN
                | CREATE DATABASE IDENTIFIER

column_definition_list : column_definition
                      | column_definition_list COMMA column_definition

column_definition : IDENTIFIER data_type constraint_list_opt

data_type : INTEGER
         | VARCHAR LEFT_PAREN NUMBER_LITERAL RIGHT_PAREN
         | CHAR LEFT_PAREN NUMBER_LITERAL RIGHT_PAREN
         | BOOLEAN
         | FLOAT
         | DOUBLE
         | DATE
         | TIMESTAMP
         | TEXT
         | BLOB

constraint_list_opt : constraint_list
                   | empty

constraint_list : constraint
               | constraint_list constraint

constraint : PRIMARY KEY
          | NOT NULL
          | NULL
```

### DROP Statement Grammar

```
drop_statement : DROP TABLE IDENTIFIER
              | DROP DATABASE IDENTIFIER
```

### Expression Grammar

```
expression : or_expression

or_expression : and_expression
             | or_expression OR and_expression

and_expression : equality_expression
              | and_expression AND equality_expression

equality_expression : comparison_expression
                   | equality_expression EQUALS comparison_expression
                   | equality_expression NOT_EQUALS comparison_expression
                   | equality_expression IS NULL
                   | equality_expression IS NOT NULL

comparison_expression : primary_expression
                     | comparison_expression LESS_THAN primary_expression
                     | comparison_expression LESS_EQUAL primary_expression
                     | comparison_expression GREATER_THAN primary_expression
                     | comparison_expression GREATER_EQUAL primary_expression
                     | comparison_expression LIKE STRING_LITERAL
                     | comparison_expression IN LEFT_PAREN value_list RIGHT_PAREN

primary_expression : column_reference
                  | STRING_LITERAL
                  | NUMBER_LITERAL
                  | BOOLEAN_LITERAL
                  | NULL
                  | LEFT_PAREN expression RIGHT_PAREN
                  | NOT primary_expression
                  | primary_expression PLUS primary_expression
                  | primary_expression MINUS primary_expression
                  | primary_expression ASTERISK primary_expression
                  | primary_expression DIVIDE primary_expression
```

### Function Call Grammar

```
function_call : COUNT LEFT_PAREN ASTERISK RIGHT_PAREN
             | COUNT LEFT_PAREN column_reference RIGHT_PAREN
             | SUM LEFT_PAREN column_reference RIGHT_PAREN
             | AVG LEFT_PAREN column_reference RIGHT_PAREN
             | MAX LEFT_PAREN column_reference RIGHT_PAREN
             | MIN LEFT_PAREN column_reference RIGHT_PAREN
```

### Column Reference Grammar

```
column_reference : IDENTIFIER
                | IDENTIFIER PERIOD IDENTIFIER
```

### List Grammar

```
column_reference_list : column_reference
                     | column_reference_list COMMA column_reference

order_item_list : order_item
               | order_item_list COMMA order_item

order_item : column_reference
          | column_reference ASC
          | column_reference DESC
```

### Empty Production

```
empty : /* empty */
```

## Operator Precedence

The parser implements the following operator precedence (from lowest to highest):

1. **OR** (logical OR)
2. **AND** (logical AND)
3. **=, !=, <, <=, >, >=, LIKE, IN, IS NULL, IS NOT NULL** (comparison)
4. **+, -** (arithmetic addition/subtraction)
5. ***, /** (arithmetic multiplication/division)
6. **NOT** (logical NOT)
7. **()** (parentheses for grouping)

## Token Definitions

### Keywords

```
SELECT, FROM, WHERE, INSERT, UPDATE, DELETE, CREATE, DROP
INTO, VALUES, SET, TABLE, DATABASE, DISTINCT, GROUP, BY
HAVING, ORDER, ASC, DESC, LIMIT, OFFSET, AND, OR, NOT
LIKE, IN, IS, NULL, PRIMARY, KEY, INTEGER, VARCHAR, CHAR
BOOLEAN, FLOAT, DOUBLE, DATE, TIMESTAMP, TEXT, BLOB
TRUE, FALSE, AS
```

### Operators

```
EQUALS: '='
NOT_EQUALS: '!='
LESS_THAN: '<'
LESS_EQUAL: '<='
GREATER_THAN: '>'
GREATER_EQUAL: '>='
PLUS: '+'
MINUS: '-'
ASTERISK: '*'
DIVIDE: '/'
```

### Punctuation

```
COMMA: ','
SEMICOLON: ';'
LEFT_PAREN: '('
RIGHT_PAREN: ')'
PERIOD: '.'
```

### Literals

```
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*
STRING_LITERAL: '[^']*' (with escape support)
NUMBER_LITERAL: [0-9]+(\.[0-9]+)?
BOOLEAN_LITERAL: TRUE|FALSE
```

## Grammar Ambiguities and Resolutions

### 1. Column List vs Asterisk

The grammar distinguishes between `*` and column lists:

```
column_list : ASTERISK
           | column_expression_list
```

**Resolution**: The parser checks the token type to determine if it's an asterisk or a column expression list.

### 2. Table Aliases

Two forms of table aliases are supported:

```
table_reference : IDENTIFIER AS IDENTIFIER  -- explicit AS
               | IDENTIFIER IDENTIFIER      -- implicit alias
```

**Resolution**: The parser uses `len(p)` to distinguish between the two forms.

### 3. Empty Productions

Optional clauses use empty productions:

```
where_clause_opt : WHERE expression
                | empty
```

**Resolution**: The parser uses a sentinel value (`"EMPTY_SENTINEL"`) to distinguish empty productions from actual content.

### 4. Function Call Arguments

Function calls can have different argument types:

```
function_call : COUNT LEFT_PAREN ASTERISK RIGHT_PAREN
             | COUNT LEFT_PAREN column_reference RIGHT_PAREN
```

**Resolution**: The parser checks the content of the argument to determine the type.

## AST Generation

The grammar rules defined above are used by the parser to generate an Abstract Syntax Tree (AST) that represents the structure of SQL queries. Each grammar production corresponds to specific AST nodes that contain the parsed information.

For detailed information about the AST node structure and how grammar rules map to AST nodes, see the **[Parser Overview](parser.md)** document.

## Error Recovery

### 1. Token-Level Recovery

- **Invalid Characters**: Lexer reports illegal characters with position information
- **Unterminated Strings**: Lexer detects unterminated string literals
- **Unterminated Comments**: Lexer detects unterminated multi-line comments

### 2. Syntax-Level Recovery

- **Missing Tokens**: Parser reports missing required tokens
- **Unexpected Tokens**: Parser reports unexpected tokens with suggestions
- **End of Input**: Parser handles unexpected end of input gracefully

### 3. Error Reporting

All errors include:
- **Error Type**: Lexical or syntax error
- **Position**: Line number and column position
- **Context**: What was expected vs what was found
- **Suggestion**: Possible fixes when applicable



## Grammar Extensions

### Adding New SQL Features

To extend the grammar with new features:

1. **Add Tokens** in `src/parser/lexer.py`:
   ```python
   def t_NEW_KEYWORD(t):
       r'NEW_KEYWORD'
       return t
   ```

2. **Add Grammar Rules** in `src/parser/parser.py`:
   ```python
   def p_new_statement(p):
       """new_statement : NEW_KEYWORD expression"""
       p[0] = NewStatement(expression=p[2])
   ```

3. **Create AST Nodes** in `src/parser/ast.py`:
   ```python
   class NewStatement(ASTNode):
       def __init__(self, expression):
           self.expression = expression
   ```

4. **Update Tests** in `tests/unit/test_parser.py`

### Best Practices for Extensions

- **Follow PLY Conventions**: Use `p_` prefix for parser rules
- **Handle Ambiguities**: Explicitly handle grammar ambiguities
- **Error Handling**: Provide meaningful error messages
- **Testing**: Add comprehensive tests for new features
- **Documentation**: Update this grammar reference

## Performance Considerations

### Grammar Optimization

- **LALR(1) Parsing**: Efficient bottom-up parsing algorithm
- **Token Caching**: PLY caches generated parsing tables
- **Minimal Conflicts**: Grammar designed to minimize shift/reduce conflicts

### Memory Usage

- **AST Size**: ~2-5KB per typical query
- **Parser State**: Minimal memory overhead
- **Token Storage**: Efficient token representation

### Parsing Speed

- **Simple Queries**: < 1ms
- **Complex Queries**: 1-5ms
- **Large Queries**: 5-10ms

## Related Documentation

- **[Parser API Reference](../api/parser.md)**: Complete API documentation
- **[Parser Overview](parser.md)**: High-level parser introduction and AST structure
- **[PLY Documentation](https://www.dabeaz.com/ply/)**: Official PLY documentation
- **[SQL Standard](https://www.iso.org/standard/63555.html)**: ISO/IEC 9075 SQL standard

---

This grammar reference provides the complete specification for the SQL parser. For implementation details and usage examples, see the [Parser API Reference](../api/parser.md).
