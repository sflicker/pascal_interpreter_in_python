from pathlib import Path
import sys
import os

from .interpreter import Interpreter
from .error_code import ErrorCode, LexerError, ParserError, SemanticError, PascalRuntimeError
from .simple_interpreter import SimpleInterpreter
from .tokenizer import Tokenizer
from .parser import Parser
#from pascal_symbol import SymbolTableBuilder
from .semantic_analyzer import SemanticAnalyzer

import json


TEST_FILES_DIR = Path(__file__).resolve().parents[2] / "test" / "test_files"


def is_verbose():
    return os.environ.get("PASCAL_TEST_VERBOSE") == "1"

# tests = [
#     ["1 + 1", 2],
#     ["8/16", 0.5],
#     ["3 -(-1)", 4],
#     ["2 + -2", 0],
#     ["10- 2- -5", 13],
#     ["(((10)))", 10],
#     ["3 * 5", 15],
#     ["-7 * -(6 / 3)", 14]
# ]
#
# for test in tests:
#     Test.assert_equals(calc(test[0]), test[1])

# program = """
# Program part10;
# VAR
#     number       : INTEGER;
#     a, b, c, x   : INTEGER;
#     y            : REAL;
# BEGIN
#     begin
#         number := 2;
#         a := number;
#         b := 10 * a + 10 * NUMBER DIV 4;
#         c := a - -b;
#     EnD;
#     X := 11;
#     y := 20 / 7 + 3.14;
#
# END.
# """


def trace(enabled, *args):
    if enabled:
        print(*args, file=sys.stderr)


def run_expression(expression, *, trace_tokens=False, verbose=False):
    trace(verbose, "-------expression:", expression)
    tokenizer = Tokenizer(expression)
    tokens = tokenizer.get_tokens()
    trace(trace_tokens, "tokens")
    if trace_tokens:
        print(*tokens, sep='\n', file=sys.stderr)

    trace(verbose, "\nParsing")
    parser = Parser(tokens)
    tree = parser.parse_expression()

    trace(verbose, "\nInterpreting")
    simple_interpreter = SimpleInterpreter(tree)
    rv = simple_interpreter.interpret()
    trace(verbose, "\nResult", rv)
    trace(verbose, expression, " = ", rv)
    return rv

def run_statement(statement, *, trace_tokens=False, verbose=False):
#    print("statement", statement)
    tokenizer = Tokenizer(statement)
    tokens = tokenizer.get_tokens()
    trace(trace_tokens, "tokens")
    if trace_tokens:
        print(*tokens, sep='\n', file=sys.stderr)

    trace(verbose, "\nParsing")
    parser = Parser(tokens)
    tree = parser.parse_statement()

    trace(verbose, "\nInterpreting")
    simple_interpreter = SimpleInterpreter(tree)
    rv = simple_interpreter.interpret()
#    print("\nResults")
#    print(rv)
#    print(simple_interpreter.results)
#    print(simple_interpreter.GLOBAL_MEMORY)
    return simple_interpreter.GLOBAL_MEMORY



def run_program(program, *, trace_tokens=False, verbose=False, source_name=None):

    # print("----------Program:\n", program)
    tokenizer = Tokenizer(program)
    try:
        tokens = tokenizer.get_tokens()
    except(LexerError) as e:
        trace(verbose, e.message)
        #sys.exit(1)
        error_code = e.error_code or ErrorCode.UNKNOWN_ERROR
        return ({}, str(error_code.values[1]), 1)

    trace(trace_tokens, "tokens")
    if trace_tokens:
        print(*tokens, sep='\n', file=sys.stderr)

    trace(verbose, "\nParsing")
    try:
        parser = Parser(tokens)
        tree = parser.parse()
    except ParserError as e:
        trace(verbose, e.message)
        #sys.exit(1)
        return ({}, str(e.error_code.values[1]), 1)

#    print("Parsed Tree")
#    ast_printer = ASTPrinter(tree)
#    ast_printer.print()

    trace(verbose, "\nCreating Symbol Table")
    # symtab_builder = SymbolTableBuilder()
    # symtab_builder.visit(tree)
#    print('\nSymbol Table Contents')
    # print(symtab_builder.symtab)

    analyzer = SemanticAnalyzer(tree)
    try:
        analyzer.analyze()
    except SemanticError as e:
        trace(verbose, e.message)
        #sys.exit(1)
        return ({}, str(e.error_code.values[1]), 1)

#    print(analyzer.current_scope)

    file_base_dir = Path(source_name).resolve().parent if source_name is not None else None
    interpreter = Interpreter(tree, file_base_dir=file_base_dir)
    trace(verbose, "\n\n------Interpreting Program")
    try:
        (result, output) = interpreter.interpret()
    except PascalRuntimeError as e:
        trace(verbose, e.message)
        return ({}, str(e.error_code.values[1]), 1)
    trace(verbose, "------Finished Interpreting Program")
#    print(str(result))
    trace(verbose, "------Program Output")
    trace(verbose, output)

    return (result.members, output, 0)
    # print(interpreter.GLOBAL_MEMORY)
    #
    # print('')
    # print('-------Run-time GLOBAL_MEMORY contents:')
    # for k,v in sorted(interpreter.GLOBAL_MEMORY.items()):
    #     print('{} = {}'.format(k,v))
#
#@test.describe("Expression Tests")
def expression_tests():
     test_directory = TEST_FILES_DIR / "expressions"
     for file in test_directory.iterdir():
         verbose = is_verbose()
         trace(verbose, "testfile", file)
         text = file.read_text()
         test = json.JSONDecoder().decode(text)
         expression = test["expr"]
         expected = test["result"]
         if isinstance(expression, list):
             expression = "\n".join(expression)
         assert run_expression(expression, trace_tokens=verbose, verbose=verbose) == expected

# #@test.describe("Statement Tests")
# def statement_tests():
#     test_directory = "test_files/statements"
#     for file in os.listdir(test_directory):
#         print("testfile", file)
#         text = open(os.path.join(test_directory, file), 'r').read()
#         test = json.JSONDecoder().decode(text)
#         statement = test["statement"]
#         if isinstance(statement, list):
#             statement = "\n".join(statement)
#         tester.assert_equals(run_statement(statement), test["expected"])


def main():
    import sys

    expression_tests()
#    statement_tests()

    # text = open("test_files/expressions/add.expr", 'r').read()
    # test = json.JSONDecoder().decode(text)
    # run_expression(test["expr"], test["result"])

    # text = open("test_files/add2.expr", 'r').read()
    # run_expression(text, 18)
    #
    # text = open("test_files/mult.expr", 'r').read()
    # run_expression(text)
    #
    # text = open("test_files/math1.expr", 'r').read()
    # run_expression(text)
    #
    # text = open("test_files/math2.expr", 'r').read()
    # run_expression(text)
    #
    # text = open("test_files/math3.expr", 'r').read()
    # run_expression(text)
    #
    # text = open("test_files/math4.expr", 'r').read()
    # run_expression(text)
    #
    # text = open("test_files/unary1.expr", 'r').read()
    # run_expression(text)
    #
    # text = open("test_files/unary2.expr", 'r').read()
    # run_expression(text)
    #
    # text = open("test_files/unary3.expr", 'r').read()
    # run_expression(text)
    #
    # text = open("test_files/statements/assign1.stat", 'r').read()
    # test = json.JSONDecoder().decode(text)
    # run_statement(test["statement"], test["expected"])
    #
    # text = open("test_files/assign2.stat", 'r').read()
    # run_statement(text)
    #
    # text = open("test_files/assign3.stat", 'r').read()
    # run_statement(text)
    #
    # text = open("test_files/compound_statement1.stat", 'r').read()
    # run_statement(text)

#    text = open("test_files/part10.pas", 'r').read()
#    run_program(text)

#    text = open("test_files/programs/simplest.pas", 'r').read()
#    run_program(text)

    text = open("test_files/programs/simplest2.pas", 'r').read()
    run_program(text)

   # text = open("test_files/if.pas", 'r').read()
   # run_program(text)

    # text = open("test_files/part11.pas", 'r').read()
    # run_program(text)
    #
    #text = open("test_files/part12.pas", 'r').read()
    #run_program(text)
    #
  #  text = open("test_files/programs/nestedscope01.pas", 'r').read()
  #  run_program(text)

#    text = open("test_files/programs/typemismatch.pas", 'r').read()
#    run_program(text)

    # text = open("test_files/programs/alpha.pas", 'r').read()
    # run_program(text)

    # text = open("test_files/programs/booleantest.pas", 'r').read()
    # run_program(text)

    # text = open("test_files/programs/booleantest2.pas", 'r').read()
    # (_, _, exitcode) = run_program(text)


    #
    # text = open("test_files/programs/part17.pas", "r").read()
    # run_program(text)

    # text = open("test_files/programs/part18.pas", "r").read()
    # run_program(text)

    #text = open("test_files/programs/func1.pas", "r").read()
    #run_program(text)

    #text = open("test_files/programs/beta.pas", "r").read()
    #run_program(text)

    #text = open("test_files/programs/global.pas", "r").read()
    #run_program(text)


    # text = open("test_files/programs/iftest.pas", "r").read()
    # run_program(text)




    #
    # text = open("test_files/nestedscopepas02.pas", 'r').read()
    # run_program(text)
    #
    # text = open("test_files/nestedscopepas02a.pas", 'r').read()
    # run_program(text)
    #
    # text = open("test_files/nestedscopes03.pas", 'r').read()
    # run_program(text)
    #
    # text = open("test_files/nestedscopes04.pas", 'r').read()
    # run_program(text)

    #text = open("test_files/programs/fortest.pas", "r").read()
    #(memory, output, exitcode) = run_program(text)

    # text = open("test_files/programs/arraytest1.pas", "r").read()
    # (memory, output, exitcode) = run_program(text)

    # text = open("test_files/programs/consttest.pas", "r").read()
    # (memory, output, exitcode) = run_program(text)

    # text = open("test_files/programs/writelntest.pas", "r").read()
    # (memory, output, exitcode) = run_program(text)

    # text = open("test_files/programs/subrangevar.pas", "r").read()
    # (memory, output, exitcode) = run_program(text)

    # text = open("test_files/programs/assign3.pas", "r").read()
    # (memory, output, exitcode) = run_program(text)

   # text = open("test_files/programs/factorial.pas", "r").read()
   # (memory, output, exitcode) = run_program(text)

    #sys.exit(exitcode)




if __name__ == '__main__':
    main()
