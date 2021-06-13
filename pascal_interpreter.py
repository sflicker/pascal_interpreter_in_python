# Instructions
# Given a mathematical expression as a string you must return the result as a number.
#
# Numbers
# Number may be both whole numbers and/or decimal numbers. The same goes for the returned result.
#
# Operators
# You need to support the following mathematical operators:
#
# Multiplication *
# Division / (as floating point division)
# Addition +
# Subtraction -
# Operators are always evaluated from left-to-right, and * and / must be evaluated before + and -.
#
# Parentheses
# You need to support multiple levels of nested parentheses, ex. (2 / (2 + 3.33) * 4) - -6
#
# Whitespace
# There may or may not be whitespace between numbers and operators.
#
# An addition to this rule is that the minus sign (-) used for negating numbers and parentheses will never be separated by whitespace. I.e all of the following are valid expressions.
#
# 1-1    // 0
# 1 -1   // 0
# 1- 1   // 0
# 1 - 1  // 0
# 1- -1  // 2
# 1 - -1 // 2
#
# 6 + -(4)   // 2
# 6 + -( -4) // 10
# And the following are invalid expressions
#
# 1 - - 1    // Invalid
# 1- - 1     // Invalid
# 6 + - (4)  // Invalid
# 6 + -(- 4) // Invalid
# Validation
# You do not need to worry about validation - you will only receive valid mathematical expressions following the above rules.
#
# Restricted APIs
# NOTE: eval and exec are disallowed in your solution.

import codewars_test as Test

import enum
from pascal_tokenizer import Tokenizer
from pascal_tokenizer import TokenType

from pascal_parser import Parser


#####################
## AST visitor
#####################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        pass
#        raise Exception('No visit_{} method'.format(type(node).__name__))

###########################
## Symbols and Symbol Table
###########################

class Symbol(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

class VarSymbol(Symbol):
    def __init__(self, name, type):
        super().__init__(name, type)

    def __str__(self):
        return '<{name}:{type}>'.format(name=self.name, type=self.type)

    __repr__ = __str__

class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

    __repr = __str__

class SymbolTable(object):
    def __init__(self):
        self._symbols = {}
        self._init_builtins()

    def _init_builtins(self):
        self.define(BuiltinTypeSymbol('INTEGER'))
        self.define(BuiltinTypeSymbol('REAL'))
        self.define(BuiltinTypeSymbol('STRING'))

    def __str__(self):
        s = 'Symbols: {symbols}'.format(
            symbols = [value for value in self._symbols.values()]
        )
        return s

    __repr__ = __str__

    def define(self, symbol):
        print('Define: %s' % symbol)
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        print('Lookup: %s' % name)
        symbol = self._symbols.get(name)
        # 'symbol' is either an instance of the Symbol class or None
        return symbol

#############################
### SymbolTableBuilder
#############################

class SymbolTableBuilder(NodeVisitor):
    def __init__(self):
        self.symtab = SymbolTable()

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_ProcedureDecl(self, node):
        pass

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_BinOp(self, node):
        self.visit(node.lhs)
        self.visit(node.rhs)

    def visit_Num(self, node):
        pass

    def visit_String(self, node):
        pass

    def visit_UnaryOp(self, node):
        self.visit(node.operand)

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.symtab.lookup(type_name)
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)
        self.symtab.define(var_symbol)

    def visit_Assign(self, node):
        var_name = node.lhs.value
        var_symbol = self.symtab.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))
        self.visit(node.rhs)

    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.symtab.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))




###########################
## Interpreter
###########################
class Interpreter(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.GLOBAL_MEMORY = {}

    def interpret(self):
        tree = self.tree
        if tree is None:
            return ''
        return self.visit(tree)

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_ProcedureDecl(self, node):
        pass

    def visit_VarDecl(self, node):
        pass

    def visit_Type(self, node):
        pass

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        var_name = node.lhs.value
        var_value = self.visit(node.rhs)
        self.GLOBAL_MEMORY[var_name] = var_value

    def visit_Var(self, node):
        var_name = node.value
        var_value = self.GLOBAL_MEMORY.get(var_name)
        if var_value is None:
            raise Exception("Unknown Symbol " + var_name)
        else:
            return var_value

    def visit_Writeln(self, node):

        arg = node.arguments
        l = []
        while arg is not None:
            l.append(str(self.visit(arg)))
            arg = arg.next

        print("".join(l))

    def visit_Num(self, node):
        return node.number

    def visit_String(self, node):
        return node.value.value

    def visit_BinaryOp(self, node):
        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)

        if node.token.type == TokenType.PLUS:
            return lhs + rhs
        if node.token.type == TokenType.MINUS:
            return lhs - rhs
        if node.token.type == TokenType.MUL:
            return lhs * rhs
        if node.token.type == TokenType.REAL_DIV:
            return float(lhs / rhs)
        if node.token.type == TokenType.INTEGER_DIV:
            return lhs // rhs

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == TokenType.PLUS:
            return +self.visit(node.operand)
        elif op == TokenType.MINUS:
            return -self.visit(node.operand)

    def visit_NoOp(self, node):
        pass



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
    parser = Parser(tokens)
    tree = parser.get_parsed_tree()

    symtab_builder = SymbolTableBuilder()
    symtab_builder.visit(tree)
    print('')
    print('Symbol Table Contents')
    print(symtab_builder.symtab)

    interpreter = Interpreter(tree)
    print("Interpreting Program")
    result = interpreter.interpret()
    print("Finished Interpreting Program")
    print(result)

    print('')
    print('Run-time GLOBAL_MEMORY contents:')
    for k,v in sorted(interpreter.GLOBAL_MEMORY.items()):
        print('{} = {}'.format(k,v))


def main():
    import sys
    text = open("test_files/part10.pas", 'r').read()

    run_program(text)




if __name__ == '__main__':
    main()