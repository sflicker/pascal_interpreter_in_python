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
Ran 159 tests

OK

Test summary:
  Expressions: 10 passed, 0 failed, 10 total
  Statements: 5 passed, 0 failed, 5 total
  Programs: 134 passed, 0 failed, 134 total
  CLI: 10 passed, 0 failed, 10 total
  Combined: 159 passed, 0 failed, 159 total
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

Use `--debug` to run the Pascal source-level debugger:

```bash
./run_pascal.sh --debug path/to/program.pas
```

Debugger output is written to stderr so Pascal program output remains on stdout.
The debugger is routine-centered: when execution pauses it shows the current
program, procedure, or function activation and a small source window around the
current line.

Debugger commands:

- `step` / `s`: execute one debuggable statement, stepping into calls
- `next` / `n`: execute one debuggable statement, stepping over calls
- `continue` / `c`: run until the next breakpoint or program end
- `break <line>` / `b <line>`: set a line breakpoint
- `break`: list breakpoints
- `clear <line>`: remove a line breakpoint
- `locals`: show variables in the current activation record
- `print <name>` / `p <name>`: print a visible variable
- `stack`: show active program/procedure/function frames
- `where` / `w`: redisplay the current source location
- `quit` / `q`: stop execution

When execution completes in debug mode, the debugger displays `Program
finished.` and waits for Enter before returning to the shell. If parsing or
semantic analysis fails before execution starts, `--debug` prints the diagnostic
message to stderr.

Initial debugger limitations:

- The source map assumes one Pascal source file.
- Breakpoints are line-based.
- There is no `finish`, watch expression, or conditional breakpoint
  support yet.

Pascal `READ` and `READLN` consume standard input. They can be used
interactively or with redirected input:

```bash
printf '85\n' | ./run_pascal.sh examples/LetterGrade.pas
```

`READ` consumes input tokens and leaves the rest of the current line available.
`READLN` reads its arguments and then discards the rest of the current line.
Input conversion is based on the target variable type: `INTEGER`, `REAL`,
`CHAR`, `BOOLEAN`, and `STRING` are supported. `READLN` may also be used without
arguments to skip the rest of the current input line.

Text file variables use `TEXT` and the standard lifecycle routines `ASSIGN`,
`RESET`, `REWRITE`, `APPEND`, `CLOSE`, `ERASE`, `RENAME`, and `FLUSH`. `READ`,
`READLN`, `WRITE`, and `WRITELN` accept a `TEXT` variable as their first
argument for file-based IO:

```pascal
VAR
  f: TEXT;
  score: INTEGER;
BEGIN
  ASSIGN(f, 'scores.txt');
  RESET(f);
  READLN(f, score);
  CLOSE(f);

  ASSIGN(f, 'report.txt');
  REWRITE(f);
  WRITELN(f, score + 1:5);
  APPEND(f);
  WRITELN(f, 'done');
  CLOSE(f);
END.
```

When a Pascal source filename is known, relative file paths are resolved against
that source file's directory. Otherwise, relative paths use the current working
directory.

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

- `CONST` declarations for integer, real, string, boolean, and named constant
  values
- Built-in constants: `MAXINT`, `MININT`, and `PI`
- Numeric `LABEL` declarations for same-block `GOTO`
- `VAR` declarations
- Multiple variables in one declaration, for example `a, b: INTEGER;`
- Simple scalar type aliases, for example `type Count = Integer;`
- Simple subrange type aliases, for example `type Range = 1..10;`
- Array index ranges using named constants, for example
  `array [Low..High] of Integer;`
- Array index ranges using named subrange types, for example
  `type Index = 1..10; ... array [Index] of Integer;`
- Enumerated type declarations, for example `type Direction = (North, East,
  South, West);`
- Record type declarations with scalar and nested record fields
- Set type declarations, for example `set of Integer;`
- Pointer type declarations, including recursive record pointers such as
  `type NodePtr = ^Node;`
- `TEXT` file variable declarations
- Procedure declarations
- Function declarations
- Procedure and function forward declarations with `FORWARD`
- Local variables inside procedure/function blocks
- Procedure/function parameters passed by value
- Procedure/function `VAR` parameters passed by reference
- Simple one-dimensional array declarations, for example
  `arr: array [1..10] of Integer;`
- Multi-dimensional array declarations, for example
  `grid: array [1..2, 1..3] of Integer;`
- Runtime bounds checking for arrays with literal subrange bounds
- Simple subrange variable declarations, for example `a: 1..10;`
- Runtime bounds checking for integer subrange variables
- Field access and assignment for records, for example `person.name := "Ada";`
- Same-scope duplicate declaration checks for constants, types, variables,
  routines, parameters, enum values, and record fields

### Types

- `INTEGER`
- `REAL`
- `STRING`
- `BOOLEAN`
- `CHAR`
- `RECORD`
- `TEXT`
- Set types
- Pointer types
- Enumerated types

### Expressions and Operators

- Integer and real numeric literals
- String literals
- Pascal-style doubled delimiters inside string literals, for example
  `'Ada''s note'` and `"She said ""hello"""`
- Character literals: single-quoted one-character literals such as `'A'`
- Pascal-style doubled delimiters inside character literals, for example `''''`
- Boolean literals: `TRUE`, `FALSE`
- `NIL` pointer literal
- Enumerated constants
- Set literals, for example `[1, 3, 5]` and `['a'..'z']`
- Variables and constants
- Parenthesized expressions
- Unary `+` and `-`
- Arithmetic: `+`, `-`, `*`, `/`, `DIV`, `MOD`
- Comparisons: `=`, `<>`, `>`, `>=`, `<`, `<=`
- Set membership with `IN`
- Set union, difference, and intersection with `+`, `-`, and `*`
- Boolean operators: `AND`, `OR`, unary `NOT`
- Function calls in expressions
- `ORD`, `PRED`, and `SUCC` support enumerated values
- `EOF` and `EOLN` return boolean values for `TEXT` input streams
- `LENGTH`, `COPY`, `POS`, and `CONCAT` support common string operations

### Statements

- Assignment with `:=`
- Assignment compatibility allows `CHAR` values into `STRING` variables and
  one-character string literals into `CHAR` variables
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
- Standard functions: `ABS`, `SQR`, `ODD`, `ORD`, `CHR`, `PRED`, `SUCC`,
  `TRUNC`, `ROUND`, `SQRT`, `EXP`, `LN`, `SIN`, `COS`, `ARCTAN`, `EOF`,
  `EOLN`, `LENGTH`, `COPY`, `POS`, and `CONCAT`
- String mutation routines: `DELETE` and `INSERT`
- Pointer lifecycle routines: `NEW`, `DISPOSE`
- `WRITE(...)`
- `WRITELN(...)`
- Formatted output fields for `WRITE` and `WRITELN`, for example
  `WRITE(value:width)` and `WRITE(real_value:width:precision)`
- `READ(...)`
- `READLN(...)`
- File lifecycle routines: `ASSIGN`, `RESET`, `REWRITE`, `APPEND`, `CLOSE`,
  `ERASE`, `RENAME`, and `FLUSH`
- File-based `READ`, `READLN`, `WRITE`, and `WRITELN` with a leading `TEXT`
  argument
- Single-record `WITH ... DO` statements

### Runtime Behavior

- Scoped symbol tables are used during parsing and semantic analysis
- Runtime execution uses activation records and a call stack
- Procedures and functions can access variables from enclosing activation records
- `VAR` parameters alias the caller's variable, so assignments update the
  caller's activation record
- Function return values are assigned through the function name, following
  Pascal style
- Pascal program output is captured by the interpreter and returned to the CLI or
  test harness
- `TEXT` file handles are scoped runtime values; relative file paths resolve
  against the Pascal source file directory when available
- Pointer values allocated by `NEW` can be dereferenced with `^`, including
  record field access such as `node^.value`
- `NIL` and disposed pointer dereferences raise runtime errors
- Lexer, parser, semantic, and runtime errors return non-zero exit codes without
  Python tracebacks. The CLI reports diagnostics to stderr and reserves stdout
  for successful Pascal program output. `--debug` reports pre-execution syntax
  diagnostics before the debugger is created.

## Not Currently Supported or Incomplete

The grammar reference in `doc/pascal_grammar.bnf` describes a broader target
than the current implementation. These features are not implemented or are only
partially implemented:

- Full standard Pascal grammar
- Command-line arguments exposed inside Pascal programs
- Cross-block or cross-procedure `GOTO`
- Full standard Pascal set semantics, including packed sets
- Full standard Pascal pointer semantics beyond `NIL`, `NEW`, `DISPOSE`, `^`,
  and record field dereference
- Binary files and typed `FILE OF ...` declarations
- Procedure types and procedure variables, including calls such as
  `test1(@writeint)`
- Standard library routines beyond `ABS`, `SQR`, `ODD`, `ORD`, `CHR`,
  `PRED`, `SUCC`, `TRUNC`, `ROUND`, `SQRT`, `EXP`, `LN`, `SIN`, `COS`,
  `ARCTAN`, `EOF`, `EOLN`, `LENGTH`, `COPY`, `POS`, `CONCAT`, basic console
  and file-based `READ`, `READLN`, `WRITE`, and `WRITELN`, `DELETE`,
  `INSERT`, `ASSIGN`, `RESET`, `REWRITE`, `APPEND`, `CLOSE`, `ERASE`,
  `RENAME`, `FLUSH`, `NEW`, and `DISPOSE`
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
│       ├── debugger.py
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

`parser.py` is a recursive-descent parser. It consumes the token list, builds
AST nodes from `pascal_ast.py`, and performs declaration-time checks that need
the parser's symbol table, such as duplicate declarations and forward routine
registration.

### Semantic Analyzer

`semantic_analyzer.py` walks the AST before execution. It checks declared
identifiers, procedure/function argument counts, and type compatibility.

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
- `test_cli.py` covers the command-line script, trace flags, and debugger
  command streams

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
