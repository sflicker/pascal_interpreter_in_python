import os
import sys

from interpreter import Interpreter
from error_code import LexerError, ParserError, SemanticError
from simple_interpreter import SimpleInterpreter
from tokenizer import Tokenizer
from parser import Parser
#from pascal_symbol import SymbolTableBuilder
from semantic_analyzer import SemanticAnalyzer


def run_program(program):

    # print("----------Program:\n", program)
    tokenizer = Tokenizer(program)
    try:
        tokens = tokenizer.get_tokens()
    except(LexerError) as e:
        print(e.message)
        #sys.exit(1)
        return ({}, str(e.error_code.values[1]), 1)

    print("tokens")
    print(*tokens, sep='\n')

#    print("\nParsing")
    try:
        parser = Parser(tokens)
        tree = parser.parse()
    except ParserError as e:
        print(e.message)
        #sys.exit(1)
        return ({}, str(e.error_code.values[1]), 1)

#    print("Parsed Tree")
#    ast_printer = ASTPrinter(tree)
#    ast_printer.print()

#    print("\nCreating Symbol Table")
    # symtab_builder = SymbolTableBuilder()
    # symtab_builder.visit(tree)
#    print('\nSymbol Table Contents')
    # print(symtab_builder.symtab)

    analyzer = SemanticAnalyzer(tree)
    try:
        analyzer.analyze()
    except SemanticError as e:
        print(e.message)
        #sys.exit(1)
        return ({}, str(e.error_code.values[1]), 1)

#    print(analyzer.current_scope)

    interpreter = Interpreter(tree)
#    print("\n\n------Interpreting Program")
    (result, output) = interpreter.interpret()
#    print("------Finished Interpreting Program")
#    print(str(result))
    print("------Program Output")
    print(output)

    return (result.members, output, 0)
    # print(interpreter.GLOBAL_MEMORY)
    #
    # print('')
    # print('-------Run-time GLOBAL_MEMORY contents:')
    # for k,v in sorted(interpreter.GLOBAL_MEMORY.items()):
    #     print('{} = {}'.format(k,v))


def main(file):
    print(file)
    program = open(file, 'r').read()
    print("Program to execute")
    print()
    print(program)
    print()
    print("Output")

    run_program(program)



if __name__ == '__main__':
    main(sys.argv[1])
