import sys
import argparse
from pathlib import Path

from .interpreter import Interpreter
from .error_code import ErrorCode, LexerError, ParserError, SemanticError, PascalRuntimeError
from .tokenizer import Tokenizer
from .parser import Parser
#from pascal_symbol import SymbolTableBuilder
from .semantic_analyzer import SemanticAnalyzer
from .debugger import Debugger, SourceMap


def trace(enabled, *args):
    if enabled:
        print(*args, file=sys.stderr)


def run_program(
    program,
    *,
    trace_tokens=False,
    verbose=False,
    interactive_input=False,
    debug=False,
    source_name=None,
    report_errors=False,
):

    tokenizer = Tokenizer(program)
    try:
        tokens = tokenizer.get_tokens()
    except(LexerError) as e:
        trace(report_errors or verbose or debug, e.message)
        error_code = e.error_code or ErrorCode.UNKNOWN_ERROR
        return ({}, str(error_code.values[1]), 1)

    trace(trace_tokens, "tokens")
    if trace_tokens:
        print(*tokens, sep='\n', file=sys.stderr)

    trace(verbose, "Parsing")
    try:
        parser = Parser(tokens)
        tree = parser.parse()
    except ParserError as e:
        trace(report_errors or verbose or debug, e.message)
        return ({}, str(e.error_code.values[1]), 1)

#    print("Parsed Tree")
#    ast_printer = ASTPrinter(tree)
#    ast_printer.print()

    trace(verbose, "Analyzing")
    # symtab_builder = SymbolTableBuilder()
    # symtab_builder.visit(tree)
#    print('\nSymbol Table Contents')
    # print(symtab_builder.symtab)

    analyzer = SemanticAnalyzer(tree)
    try:
        analyzer.analyze()
    except SemanticError as e:
        trace(report_errors or verbose or debug, e.message)
        return ({}, str(e.error_code.values[1]), 1)

#    print(analyzer.current_scope)

    debugger = None
    if debug:
        debugger = Debugger(SourceMap(source_name, program))

    file_base_dir = Path(source_name).resolve().parent if source_name is not None else None
    interpreter = Interpreter(tree, interactive_input=interactive_input, debugger=debugger, file_base_dir=file_base_dir)
    trace(verbose, "Interpreting")
    try:
        (result, output) = interpreter.interpret()
    except PascalRuntimeError as e:
        trace(report_errors or verbose or debug, e.message)
        return ({}, str(e.error_code.values[1]), 1)
    trace(verbose, "Finished interpreting")

    return (result.members if result is not None else {}, output, 0)
    # print(interpreter.GLOBAL_MEMORY)
    #
    # print('')
    # print('-------Run-time GLOBAL_MEMORY contents:')
    # for k,v in sorted(interpreter.GLOBAL_MEMORY.items()):
    #     print('{} = {}'.format(k,v))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Pascal Interpreter")
    parser.add_argument("--verbose", action="store_true", help="print high-level execution trace to stderr")
    parser.add_argument("--trace-tokens", action="store_true", help="print tokenizer output to stderr")
    parser.add_argument("--trace-source", action="store_true", help="print the source program to stderr before running")
    parser.add_argument("--trace-all", action="store_true", help="enable all trace output")
    parser.add_argument("--debug", action="store_true", help="run with the interactive Pascal debugger")
    parser.add_argument("file", help="Pascal source file")

    args = parser.parse_args(argv)

    program = open(args.file, 'r').read()
    verbose = args.verbose or args.trace_all
    trace_tokens = args.trace_tokens or args.trace_all
    trace_source = args.trace_source or args.trace_all

    trace(verbose, "Args:", args)
    if trace_source:
        trace(True, "Program to execute")
        trace(True, "")
        trace(True, program)
        trace(True, "")

    (_, output, exitcode) = run_program(
        program,
        trace_tokens=trace_tokens,
        verbose=verbose,
        interactive_input=sys.stdin.isatty(),
        debug=args.debug,
        source_name=args.file,
        report_errors=True,
    )
    if exitcode == 0:
        print(output, end="")
    return exitcode


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
