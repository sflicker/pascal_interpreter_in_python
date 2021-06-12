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

class Interpreter(object):
    def __init__(self):
        self.SYMBOL_TABLE = {}
        pass

    def interpret(self, ast):
        if ast.type == "Program":
            self.interpret(ast.block)
            return self.SYMBOL_TABLE

        if ast.type == "Block":
            for declaration in ast.declarations:
                self.interpret(declaration)
            self.interpret(ast.compound_statement)

        if ast.type == "ProcedureDecl":
            return

        if ast.type == "VarDecl":
            return

        if ast.type == "Type":
            return

        if ast.type == "Compound":
            for child in ast.children:
                self.interpret(child)
            return self.SYMBOL_TABLE
        if ast.type == "Assign":
            var_name = ast.left.value
            self.SYMBOL_TABLE[var_name] = self.interpret(ast.right)
            return
        if ast.type == "Variable":
            var_name = ast.value
            val = self.SYMBOL_TABLE.get(var_name)
            if val is None:
                raise Exception("Unknown Symbol " + var_name)
            else:
                return val
        if ast.type == "Number":
            return float(ast.token.value)
        if ast.type == "Negation":
            operand = self.interpret(ast.operand)
            return -operand
        if ast.type == "Op":
            lhs = self.interpret(ast.lhs)
            rhs = self.interpret(ast.rhs)
            if ast.token.type == TokenType.PLUS:
                return lhs + rhs
            if ast.token.type == TokenType.MINUS:
                return lhs - rhs
            if ast.token.type == TokenType.MUL:
                return lhs * rhs
            if ast.token.type == TokenType.REAL_DIV:
                return float(lhs / rhs)
            if ast.token.type == TokenType.INTEGER_DIV:
                return lhs // rhs


def run_program(program):
    print("expression", program)
    tokenizer = Tokenizer(program)
    tokens = tokenizer.get_tokens()
    print("tokens")
    print(*tokens, sep='\n')
    parser = Parser(tokens)
    ast = parser.get_parsed_tree()
    solver = Interpreter()
    symbol_table = solver.interpret(ast)
    print(symbol_table)
    return symbol_table


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
