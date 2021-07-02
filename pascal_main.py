import os

from pascal_interpreter import Interpreter
from pascal_simple_interpreter import SimpleInterpreter
from pascal_tokenizer import Tokenizer
from pascal_parser import Parser
#from pascal_symbol import SymbolTableBuilder
from pascal_semantic_analyzer import SemanticAnalyzer
import codewars_test as Test
import json

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

def run_expression(expression, expected):
    print("expression:", expression, ", expected:", expected)
    tokenizer = Tokenizer(expression)
    tokens = tokenizer.get_tokens()
    # print("tokens")
    # print(*tokens, sep='\n')

    # print("\nParsing")
    parser = Parser(tokens)
    tree = parser.parse_expression()

    #print("\nInterpreting")
    simple_interpreter = SimpleInterpreter(tree)
    rv = simple_interpreter.interpret()
    print("\nResults", rv)
    Test.assert_equals(rv, expected)

def run_statement(statement, expected):
    print("statement", statement)
    tokenizer = Tokenizer(statement)
    tokens = tokenizer.get_tokens()
    print("tokens")
    print(*tokens, sep='\n')

    print("\nParsing")
    parser = Parser(tokens)
    tree = parser.parse_statement()

    print("\nInterpreting")
    simple_interpreter = SimpleInterpreter(tree)
    rv = simple_interpreter.interpret()
    print("\nResults")
    print(rv)
    print(simple_interpreter.results)
    print(simple_interpreter.GLOBAL_MEMORY)
    Test.assert_equals(simple_interpreter.GLOBAL_MEMORY, expected)

def run_program(program):

    print("expression", program)
    tokenizer = Tokenizer(program)
    tokens = tokenizer.get_tokens()
    print("tokens")
    print(*tokens, sep='\n')

    print("\nParsing")
    parser = Parser(tokens)
    tree = parser.parse()

#    print("Parsed Tree")
#    ast_printer = ASTPrinter(tree)
#    ast_printer.print()

#    print("\nCreating Symbol Table")
    # symtab_builder = SymbolTableBuilder()
    # symtab_builder.visit(tree)
#    print('\nSymbol Table Contents')
    # print(symtab_builder.symtab)

    analyzer = SemanticAnalyzer()
    try:
        analyzer.visit(tree)
    except Exception as e:
        print(e)

    print(analyzer.current_scope)

    interpreter = Interpreter(tree)
    print("\n\n------Interpreting Program")
    result = interpreter.interpret()
    print("------Finished Interpreting Program")
    print(result)
    #
    # print('')
    # print('-------Run-time GLOBAL_MEMORY contents:')
    # for k,v in sorted(interpreter.GLOBAL_MEMORY.items()):
    #     print('{} = {}'.format(k,v))


def main():
    import sys

    test_directory = "test_files/expressions"
    for file in os.listdir(test_directory):
        print("testfile", file)
        text = open(os.path.join(test_directory, file), 'r').read()
        test = json.JSONDecoder().decode(text)
        run_expression(test["expr"], test["result"])

    test_directory = "test_files/statements"
    for file in os.listdir(test_directory):
        print("testfile", file)
        text = open(os.path.join(test_directory, file), 'r').read()
        test = json.JSONDecoder().decode(text)
        run_statement(test["statement"], test["expected"])

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

    # text = open("test_files/simplest.pas", 'r').read()
    # run_program(text)

#    text = open("test_files/simplest2.pas", 'r').read()
#    run_program(text)

   # text = open("test_files/if.pas", 'r').read()
   # run_program(text)

    # text = open("test_files/part11.pas", 'r').read()
    # run_program(text)
    #
    #text = open("test_files/part12.pas", 'r').read()
    #run_program(text)
    #
    # text = open("test_files/nestedscope01.pas", 'r').read()
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





if __name__ == '__main__':
    main()