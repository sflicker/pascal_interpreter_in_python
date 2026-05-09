# Pascal Interpreter in Python

A Python implementation of an interpreter for a reduced subset of Pascal.

The project follows a classic interpreter pipeline:

```text
Pascal source -> tokenizer -> parser -> AST -> semantic analyzer -> interpreter
```

It is primarily useful as a learning project for lexing, parsing, semantic
analysis, symbol tables, scoped runtime storage, and tree-walking interpreters.

## Requirements

- Python 3.10 or newer
- No third-party runtime dependencies are required

This repository uses a `src/` layout. If the package has not been installed,
run commands with `PYTHONPATH=src:.`.

## Running the Tests

The current test suite is fixture-based and can be run with:

```bash
env PYTHONPATH=src:. python3 test/test_pascal.py
```

Expected result:

```text
Ran 24 tests

OK
```

`pytest` is not required. `python3 -m unittest discover` also works when
`PYTHONPATH=src` is set, but the output is noisier because `test/test_pascal.py`
runs its own suite at import time.

## Running a Pascal Program

The intended command-line entry point is:

```bash
env PYTHONPATH=src python3 -m pascal_interpreter path/to/program.pas
```

During development, the test harness is usually the most reliable way to run
programs:

```python
from pascal_interpreter.pascal_tester import run_program

program = """
PROGRAM Hello;
BEGIN
  WRITELN('Hello, world!');
END.
"""

memory, output, exitcode = run_program(program)
```

## Supported Pascal Features

The interpreter supports a practical subset of Pascal that is covered by the
current tests.

### Program Structure

- `PROGRAM name; ... END.`
- Optional program parameter list syntax is parsed but ignored
- `BEGIN ... END` compound statements
- Nested blocks through procedures and functions

### Declarations

- `CONST` declarations for integer, real, string, and boolean constants
- `VAR` declarations
- Multiple variables in one declaration, for example `a, b: INTEGER;`
- Procedure declarations
- Function declarations
- Local variables inside procedure/function blocks
- Procedure/function parameters passed by value

### Types

- `INTEGER`
- `REAL`
- `STRING`
- `CHAR` as a type node
- `BOOLEAN`

### Expressions and Operators

- Integer and real numeric literals
- String literals
- Boolean literals: `TRUE`, `FALSE`
- Variables and constants
- Parenthesized expressions
- Unary `+` and `-`
- Arithmetic: `+`, `-`, `*`, `/`, `DIV`
- Comparisons: `=`, `<>`, `>`, `>=`, `<`, `<=`
- Boolean operators: `AND`, `OR`, `NOT`

### Statements

- Assignment with `:=`
- `IF ... THEN ... ELSE`
- `WHILE ... DO`
- `FOR ... TO ... DO`
- `FOR ... DOWNTO ... DO`
- Procedure calls
- Function calls in expressions
- `WRITE(...)`
- `WRITELN(...)`

### Runtime Behavior

- Scoped symbol tables are used during parsing and semantic analysis
- Runtime execution uses activation records and a call stack
- Procedures and functions can access variables from enclosing activation records
- Function return values are assigned through the function name, following
  Pascal style

## Not Currently Supported or Incomplete

The grammar reference in `doc/pascal_grammar.bnf` describes a broader target
than the current implementation. These features are not implemented or are only
partially implemented:

- Full standard Pascal grammar
- `GOTO` and labels
- `REPEAT ... UNTIL`
- `CASE`
- `WITH`
- Records
- Sets
- Pointers
- Files
- Enumerated types
- User-defined type aliases are parsed only partially
- Arrays and subranges have AST/parser pieces but are not fully supported at
  semantic-analysis or runtime level
- `VAR` parameters / pass-by-reference parameters
- Procedure and function forward declarations
- Input handling is incomplete; `READ` / `READLN` are not consistently wired to
  the activation-record runtime model
- Character literal handling separate from strings
- Standard library routines beyond `WRITE` and `WRITELN`
- Robust syntax-error recovery

## Project Layout

```text
.
├── doc/
│   ├── README.md
│   └── pascal_grammar.bnf
├── src/
│   └── pascal_interpreter/
│       ├── __main__.py
│       ├── activation_record.py
│       ├── CallStack.py
│       ├── data_type.py
│       ├── error_code.py
│       ├── interpreter.py
│       ├── parser.py
│       ├── pascal.py
│       ├── pascal_ast.py
│       ├── pascal_tester.py
│       ├── semantic_analyzer.py
│       ├── simple_interpreter.py
│       ├── symbol.py
│       ├── token_type.py
│       └── tokenizer.py
└── test/
    ├── test_expression.py
    ├── test_pascal.py
    ├── test_program.py
    ├── test_statement.py
    └── test_files/
```

## Architecture

### Tokenizer

`tokenizer.py` reads source text and emits `Token` objects. It handles
identifiers, reserved words, constants, comments, strings, numbers, and
operators.

### Parser

`parser.py` is a recursive-descent parser. It consumes the token list and builds
AST nodes from `pascal_ast.py`.

### Semantic Analyzer

`semantic_analyzer.py` walks the AST before execution. It checks declared
identifiers, duplicate declarations, procedure/function argument counts, and
basic type compatibility.

### Interpreter

`interpreter.py` walks the AST and executes it. Runtime state is held in
`ActivationRecord` objects on a `CallStack`.

### Simple Interpreter

`simple_interpreter.py` is used by expression and statement tests. It skips full
Pascal program structure and allows small expressions/statements to be tested in
isolation.

## Test Fixtures

Test inputs live under `test/test_files/`.

- `expressions/*.expr` files contain JSON expression tests
- `programs/*.pas` files contain Pascal programs
- matching `programs/*.exp` files contain expected memory, output, and exit code

## Known Development Notes

- Use `python3` in this environment; `python` may not be available.
- The package is not installed by default, so use `PYTHONPATH=src:.` when running
  tests directly from the repository.
- Some modules still contain exploratory or commented code from earlier
  interpreter stages.
- The command-line entry module should be treated as development code; the
  fixture test harness is currently the better exercised path.

## Inspiration

This project was inspired by Ruslan Spivak's "Let's Build A Simple Interpreter"
series, beginning with
[Part 1](https://ruslanspivak.com/lsbasi-part1/) on Ruslan's Blog. The series
walks through building an interpreter step by step and is a useful reference for
the tokenizer, parser, AST, semantic-analysis, and interpreter ideas used here.

This repository is not an official continuation of that series. It follows the
same learning-oriented spirit and extends the Pascal interpreter in directions
that were useful for this project.
