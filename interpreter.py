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

#import codewars_test as Test

#import enum
#from pascal_tokenizer import Tokenizer
from symbol import ScopedSymbolTable, ProcedureSymbol, VarSymbol
from tokenizer import TokenType

#from pascal_parser import Parser
#from pascal_symbol import SymbolTableBuilder
from ast import NodeVisitor
#from pascal_semantic_analyzer import SemanticAnalyzer

########################
## Tree Printer
########################

class ASTPrinter(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree

    def print(self):
        self.visit(self.tree)

    def visit_Program(self, node):
        print("Program", node.name)
        self.visit(node.block)

    def visit_ProcedureDecl(self, node):
        print("ProcedureDecl", node.proc_name)
        self.visit(node.block_node)

    def visit_Block(self, node):
        print("Block")
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        print("VarDecl")
        print("var", node.var_node)
        print("type", node.type_node)

    def visit_Compound(self, node):
        print("Compound")
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        print("Assign", self.visit(node.lhs), "To", self.visit(node.rhs))

    def visit_Var(self, node):
        return node.value

    def visit_Num(self, node):
        return node.number

    def visit_String(self, node):
        return node.value

    def visit_BinaryOp(self, node):
        print(self.visit(node.lhs), node.op, self.visit(node.rhs))

    def visit_UnaryOp(self, node):
        print(node.op, self.visit(node.operand))

    def visit_Output(self, node):
        print(node.op, node.arguments)


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
        return self.visit(self.tree)

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_ProcedureDeclaration(self, node):
        pass

    def visit_VariableDeclaration(self, node):
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
        return var_value

    def visit_Output(self, node):

        l = []
        if node.arguments != None:
            for arg in node.arguments:
                l.append(str(self.visit(arg)))

        if node.op.value == "WRITELN":
            print("".join(l))
        elif node.op.value == "WRITE":
            print("".join(l), end="", flush=True)

    def visit_Input(self, node):
        for arg in node.arguments:
            inp = input()
            var_name = arg.value
            #todo fix this to handle types, hard coding int for now.
            self.GLOBAL_MEMORY[var_name] = int(inp)

    def visit_Num(self, node):
        return node.number

    def visit_String(self, node):
        return node.value.value

    def visit_BinaryOp(self, node):
        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)
        op = node.token.type

        if op == TokenType.PLUS:
            return lhs + rhs
        if op == TokenType.MINUS:
            return lhs - rhs
        if op == TokenType.MUL:
            return lhs * rhs
        if op == TokenType.REAL_DIV:
            return float(lhs / rhs)
        if op == TokenType.INTEGER_DIV:
            return lhs // rhs
        if op == TokenType.EQUAL:
            return lhs == rhs
        if op == TokenType.NOT_EQUAL:
            return lhs != rhs
        if op == TokenType.GREATER:
            return lhs > rhs
        if op == TokenType.GREATER_EQUAL:
            return lhs >= rhs
        if op == TokenType.LESS:
            return lhs < rhs
        if op == TokenType.LESS_EQUAL:
            return lhs <= rhs
        if op == TokenType.AND:
            return lhs and rhs
        if op == TokenType.OR:
            return lhs or rhs

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == TokenType.PLUS:
            return +self.visit(node.operand)
        elif op == TokenType.MINUS:
            return -self.visit(node.operand)

    def visit_NoOp(self, node):
        pass

    def visit_IFStatement(self, node):
        if (self.visit(node.expr)):
            self.visit(node.statement)
        else:
            self.visit(node.else_statement)

    def visit_WhileStatement(self, node):
        while(self.visit(node.expr)):
            self.visit(node.statement)