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
./run_tests.sh
```

Expected result:

```text
Ran 75 tests

OK

Test summary:
  Expressions: 10 passed, 0 failed, 10 total
  Statements: 5 passed, 0 failed, 5 total
  Programs: 57 passed, 0 failed, 57 total
  CLI: 3 passed, 0 failed, 3 total
  Combined: 75 passed, 0 failed, 75 total
```

Use `./run_tests.sh --verbose` to include fixture names, token traces, and other
diagnostic details. `pytest` is not required.

## Running a Pascal Program

The intended command-line entry point is:

```bash
./run_pascal.sh path/to/program.pas
```

By default, only Pascal `WRITE` and `WRITELN` output is printed to stdout. Use
trace flags to inspect interpreter internals; trace output is written to stderr:

```bash
./run_pascal.sh --verbose path/to/program.pas
./run_pascal.sh --trace-tokens path/to/program.pas
./run_pascal.sh --trace-source path/to/program.pas
./run_pascal.sh --trace-all path/to/program.pas
```

Pascal `READ` and `READLN` consume standard input. They can be used
interactively or with redirected input:

```bash
printf '85\n' | ./run_pascal.sh examples/LetterGrade.pas
```

The package can also be run directly when `PYTHONPATH` points at `src/`:

```bash
env PYTHONPATH=src python3 -m pascal_interpreter path/to/program.pas
```

During development, the test harness can run programs without printing debug
output:

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
- Numeric `LABEL` declarations for same-block `GOTO`
- `VAR` declarations
- Multiple variables in one declaration, for example `a, b: INTEGER;`
- Procedure declarations
- Function declarations
- Local variables inside procedure/function blocks
- Procedure/function parameters passed by value
- Simple one-dimensional array declarations, for example
  `arr: array [1..10] of Integer;`
- Simple subrange variable declarations, for example `a: 1..10;`

### Types

- `INTEGER`
- `REAL`
- `STRING`
- `BOOLEAN`
- `CHAR`

### Expressions and Operators

- Integer and real numeric literals
- String literals
- Character literals: single-quoted one-character literals such as `'A'`
- Boolean literals: `TRUE`, `FALSE`
- Variables and constants
- Parenthesized expressions
- Unary `+` and `-`
- Arithmetic: `+`, `-`, `*`, `/`, `DIV`, `MOD`
- Comparisons: `=`, `<>`, `>`, `>=`, `<`, `<=`
- Boolean operators: `AND`, `OR`, unary `NOT`
- Function calls in expressions

### Statements

- Assignment with `:=`
- Numeric labels, for example `100: writeln(n);`
- Same-block `GOTO`, for example `goto 100;`
- `IF ... THEN ... ELSE`
- `CASE ... OF ... ELSE ... END`
- `WHILE ... DO`
- `REPEAT ... UNTIL`
- `FOR ... TO ... DO`
- `FOR ... DOWNTO ... DO`
- Procedure calls
- Function calls in expressions
- `WRITE(...)`
- `WRITELN(...)`
- `READ(...)`
- `READLN(...)`

### Runtime Behavior

- Scoped symbol tables are used during parsing and semantic analysis
- Runtime execution uses activation records and a call stack
- Procedures and functions can access variables from enclosing activation records
- Function return values are assigned through the function name, following
  Pascal style
- Pascal program output is captured by the interpreter and returned to the CLI or
  test harness

## Not Currently Supported or Incomplete

The grammar reference in `doc/pascal_grammar.bnf` describes a broader target
than the current implementation. These features are not implemented or are only
partially implemented:

- Full standard Pascal grammar
- Command-line arguments exposed inside Pascal programs
- Cross-block or cross-procedure `GOTO`
- `WITH`
- Records
- Sets
- Pointers
- Files
- Enumerated types
- User-defined type aliases are parsed only partially and are not fully
  supported semantically
- Procedure types and procedure variables, including calls such as
  `test1(@writeint)`
- Array bounds checking
- Multi-dimensional arrays
- Named subrange constants as array index types, for example
  `array[Range] of Integer`
- `VAR` parameters / pass-by-reference parameters
- Procedure and function forward declarations
- Pascal-style escaped quotes inside string or character literals
- Standard library routines beyond `WRITE` and `WRITELN`
- Robust syntax-error recovery

## Project Layout

```text
.
├── examples/
│   ├── LetterGrade.pas
│   └── hello.pas
├── doc/
│   ├── README.md
│   └── pascal_grammar.bnf
├── pyproject.toml
├── run_pascal.sh
├── run_tests.sh
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
    ├── test_cli.py
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
- `statements/*.stat` files contain JSON statement tests
- `programs/*.pas` files contain Pascal programs
- matching `programs/*.exp` files contain expected memory, output, and exit code
- program `.exp` files can include an optional `"input"` string for tests that
  exercise `READ` or `READLN`
- `test_cli.py` covers the command-line script and trace flags

## Known Development Notes

- Use `python3` in this environment; `python` may not be available.
- The package is not installed by default, so use `PYTHONPATH=src:.` when running
  tests directly from the repository.
- Some modules still contain exploratory or commented code from earlier
  interpreter stages.
- Boolean constants evaluate to Python booleans at runtime, so output currently
  appears as `True` or `False`.
- Some unsupported syntax intentionally has expected-failure fixtures so the
  current behavior stays visible.

## Inspiration

This project was inspired by Ruslan Spivak's "Let's Build A Simple Interpreter"
series, beginning with
[Part 1](https://ruslanspivak.com/lsbasi-part1/) on Ruslan's Blog. The series
walks through building an interpreter step by step and is a useful reference for
the tokenizer, parser, AST, semantic-analysis, and interpreter ideas used here.

This repository is not an official continuation of that series. It follows the
same learning-oriented spirit and extends the Pascal interpreter in directions
that were useful for this project.
