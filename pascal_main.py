from pascal_interpreter import Interpreter
from pascal_tokenizer import Tokenizer
from pascal_parser import Parser
#from pascal_symbol import SymbolTableBuilder
from pascal_semantic_analyzer import SemanticAnalyzer

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

    # interpreter = Interpreter(tree)
    # print("\n\n------Interpreting Program")
    # result = interpreter.interpret()
    # print("------Finished Interpreting Program")
    # print(result)
    #
    # print('')
    # print('-------Run-time GLOBAL_MEMORY contents:')
    # for k,v in sorted(interpreter.GLOBAL_MEMORY.items()):
    #     print('{} = {}'.format(k,v))


def main():
    import sys
#    text = open("test_files/part10.pas", 'r').read()
#    text = open("test_files/simplest.pas", 'r').read()
#    text = open("test_files/simplest2.pas", 'r').read()
#    text = open("test_files/if.pas", 'r').read()
#    text = open("test_files/part11.pas", 'r').read()
#    text = open("test_files/part12.pas", 'r').read()
#    text = open("test_files/nestedscope01.pas", 'r').read()
#    text = open("test_files/nestedscopepas02.pas", 'r').read()
    #text = open("test_files/nestedscopepas02a.pas", 'r').read()
#    text = open("test_files/nestedscopes03.pas", 'r').read()
    text = open("test_files/nestedscopes04.pas", 'r').read()

    run_program(text)




if __name__ == '__main__':
    main()