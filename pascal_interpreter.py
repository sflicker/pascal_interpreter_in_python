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

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

class Interpreter(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.SYMBOL_TABLE = {}

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
        var_name = node.left.value
        var_value = self.visit(node.right)
        self.SYMBOL_TABLE[var_name] = var_value

    def visit_Var(self, node):
        var_name = node.value
        var_value = self.SYMBOL_TABLE.get(var_name)
        if var_value is None:
            raise Exception("Unknown Symbol " + var_name)
        else:
            return var_value

    def visit_Num(self, node):
        return node.number

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
        operand = self.visit(node.operand)
        return -operand

    def visit_NoOp(self, node):
        pass

def run_program(program):
    print("expression", program)
    tokenizer = Tokenizer(program)
    tokens = tokenizer.get_tokens()
    print("tokens")
    print(*tokens, sep='\n')
    parser = Parser(tokens)
    tree = parser.get_parsed_tree()
    interpreter = Interpreter(tree)
    result = interpreter.interpret()

    print(interpreter.SYMBOL_TABLE)


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

program = """
PROGRAM Part12;
VAR
    a : INTEGER;
    
PROCEDURE P1;
VAR
    a : REAL;
    k : INTEGER;
    
    PROCEDURE P2;
    VAR
        a, z : INTEGER;
    BEGIN {P2}
        z := 777;
    END ; {P2}

BEGIN {P1}

END; {P1}

BEGIN {Part12}
    a := 10;
END. {Part12}
"""

run_program(program)
