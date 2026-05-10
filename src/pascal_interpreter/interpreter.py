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
import io
import sys

from .CallStack import CallStack
from .activation_record import ActivationRecord, ARType
from .data_type import DataType
from .tokenizer import TokenType

#from pascal_parser import Parser
#from pascal_symbol import SymbolTableBuilder
from .pascal_ast import NodeVisitor, Program, Block, Assign, ProcedureCall, FunctionCall, \
    VariableDeclaration, LabelStatement, GotoStatement, ForStatement, RepeatUntilStatement, CaseStatement


#from pascal_semantic_analyzer import SemanticAnalyzer

########################
## Tree Printer
########################

# class ASTPrinter(NodeVisitor):
#     def __init__(self, tree):
#         self.tree = tree
#
#     def print(self):
#         self.visit(self.tree)
#
#     def visit_Program(self, node):
#         print("Program", node.name)
#         self.visit(node.block)
#
#     def visit_ProcedureDecl(self, node):
#         print("ProcedureDecl", node.proc_name)
#         self.visit(node.block_node)
#
#     def visit_Block(self, node):
#         print("Block")
#         for declaration in node.declarations:
#             self.visit(declaration)
#         self.visit(node.compound_statement)
#
#     def visit_VarDecl(self, node):
#         pass
#         print("VarDecl")
#         print("var", node.var_node)
#         print("type", node.type_node)
#
#     def visit_Compound(self, node):
#         print("Compound")
#         for child in node.children:
#             self.visit(child)
#
#     def visit_Assign(self, node):
#         print("Assign", self.visit(node.lhs), "To", self.visit(node.rhs))
#
#     def visit_Ident(self, node):
#         return node.value
#
#     def visit_Num(self, node):
#         return node.number
#
#     def visit_String(self, node):
#         return node.value
#
#     def visit_BinaryOp(self, node):
#         print(self.visit(node.lhs), node.op, self.visit(node.rhs))
#
#     def visit_UnaryOp(self, node):
#         print(node.op, self.visit(node.operand))
#
#     def visit_Output(self, node):
#         print(node.op, node.arguments)


###########################
## Interpreter
###########################
# class ProcedureDeclartion:
#     pass
#
#
# class VariableDeclartion:
#     pass


class GotoSignal(Exception):
    def __init__(self, label):
        self.label = label


class PascalInput:
    def __init__(self, stream):
        self.stream = stream
        self.line = ""
        self.pos = 0

    def read_token(self):
        while True:
            if self.pos >= len(self.line):
                self.line = self.stream.readline()
                self.pos = 0
                if self.line == "":
                    raise EOFError("No more input")

            while self.pos < len(self.line) and self.line[self.pos].isspace():
                self.pos += 1

            if self.pos < len(self.line):
                break

        start = self.pos
        while self.pos < len(self.line) and not self.line[self.pos].isspace():
            self.pos += 1
        return self.line[start:self.pos]

    def discard_line(self):
        if self.pos >= len(self.line):
            self.line = self.stream.readline()
        self.line = ""
        self.pos = 0


class Interpreter(NodeVisitor):
    def __init__(self, tree, *, interactive_input=False):
        self.tree = tree
        self.call_stack = CallStack()
        self.interactive_input = interactive_input
        self.input = PascalInput(sys.stdin)

    def interpret(self):
        self.output = io.StringIO()
        tree = self.tree
        if tree is None:
            return ''
        rv = self.visit(self.tree)

        return (rv, self.output.getvalue())

    def visit_Program(self, node: Program):
        program_name = node.name
        #print(f'ENTER: PROGRAM {program_name}')

        ar = ActivationRecord(
            name=program_name,
            ar_type=ARType.PROGRAM,
            nesting_level=1,
        )

        for decl in node.block.declarations:
            if isinstance(decl, VariableDeclaration):
                ar.set_new(decl.name, None, decl.type.data_type)

        self.call_stack.push(ar)

        self.visit(node.block)

        #print(f'LEAVE: PROGRAM {program_name}')
        #print(str(self.call_stack))

        return self.call_stack.pop()

    def visit_Block(self, node: Block):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        ar = self.call_stack.peek()
        if node.type.data_type == DataType.ARRAY:
            ar.set_new(node.name, {}, node.type.data_type)
        else:
            ar.set_new(node.name, None, node.type.data_type)

    def visit_Type(self, node):
        pass

    def visit_Compound(self, node):
        label_indexes = {
            child.label: index
            for index, child in enumerate(node.children)
            if isinstance(child, LabelStatement)
        }

        index = 0
        while index < len(node.children):
            try:
                self.visit(node.children[index])
                index += 1
            except GotoSignal as signal:
                if signal.label not in label_indexes:
                    raise
                index = label_indexes[signal.label]

    def visit_Assign(self, node: Assign):
        val = self.visit(node.rhs)

        ar = self.call_stack.peek()
        if hasattr(node.lhs, "index_expression"):
            array_name = node.lhs.name.value
            array_value = ar.get(array_name)
            array_value[str(self.visit(node.lhs.index_expression))] = val
        else:
            ar.assign_existing(node.lhs.value, val)

    def visit_LabelStatement(self, node: LabelStatement):
        self.visit(node.statement)

    def visit_GotoStatement(self, node: GotoStatement):
        raise GotoSignal(node.label)

    def visit_Ident(self, node):
        var_name = node.value

        ar = self.call_stack.peek()
        var_value = ar.get(var_name)

        return var_value

    def visit_IndexedVariable(self, node):
        ar = self.call_stack.peek()
        array_value = ar.get(node.name.value)
        return array_value.get(str(self.visit(node.index_expression)))

    def visit_Output(self, node):

        l = []
        if node.arguments != None:
            for arg in node.arguments:
                l.append(str(self.visit(arg)))

        if node.op.value == "WRITELN":
            outstr = "".join(l)
            self.output.write(outstr)
            self.output.write('\n')
        elif node.op.value == "WRITE":
            self.output.write("".join(l))

    def visit_Input(self, node):
        if self.interactive_input:
            print(self.output.getvalue(), end='', flush=True)
            self.output = io.StringIO()

        for arg in node.arguments:
            var_name = arg.value
            ar = self.call_stack.peek()
            ar.assign_existing(var_name, self.convert_input(self.input.read_token(), ar.get_type(var_name)))

        if node.op.value == "READLN":
            self.input.discard_line()

    def convert_input(self, value, data_type):
        if data_type == DataType.INTEGER:
            return int(value)
        if data_type == DataType.REAL:
            return float(value)
        if data_type == DataType.CHAR:
            return value[0]
        if data_type == DataType.BOOLEAN:
            return value.upper() == "TRUE"
        return value

    def visit_IntegerConstant(self, node):
        return node.value

    def visit_RealConstant(self, node):
        return node.value

    def visit_StringConstant(self, node):
        return node.value

    def visit_CharConstant(self, node):
        return node.value

    def visit_BooleanConstant(self, node):
        return node.value == "TRUE"

    def visit_ProcedureCall(self, node: ProcedureCall):
        proc_name = node.proc_name
        proc_symbol = node.proc_symbol

        ar = ActivationRecord(
            name=proc_name,
            ar_type=ARType.PROCEDURE,
            nesting_level=proc_symbol.scope_level + 1,
            parent_ar=self.call_stack.peek(),
        )


        # store the arguments in the activation record
        formal_params = proc_symbol.formal_params
        actual_params = node.actual_params

        for param_symbol, argument_node in zip(formal_params, actual_params):
            ar.set_new(param_symbol.name, self.visit(argument_node))

        self.call_stack.push(ar)

        #print(f'ENTER: PROCEDURE {proc_name}')
        #print(str(self.call_stack))

        #eval procedure body
        self.visit(proc_symbol.block_ast)

        #print(f'LEAVE: PROCEDURE {proc_name}')
        #print(str(self.call_stack))

        self.call_stack.pop()

    def visit_FunctionCall(self, node: FunctionCall):

        func_name = node.func_name
        func_symbol = node.func_symbol

        ar = ActivationRecord(
            name=func_name,
            ar_type=ARType.FUNCTION,
            nesting_level=func_symbol.scope_level + 1,
            parent_ar=self.call_stack.peek(),
        )


        # store the arguments in the activation record
        formal_params = func_symbol.formal_params
        actual_params = node.actual_params

        for param_symbol, argument_node in zip(formal_params, actual_params):
            ar[param_symbol.name] = self.visit(argument_node)
        # add a member with the function name for the return
        ar[func_name] = None

        self.call_stack.push(ar)

        #print(f'ENTER: FUNCTION {func_name}')
        #print(str(self.call_stack))

        #eval procedure body
        self.visit(func_symbol.block_ast)

        #get the return value from the activation record
        rv = ar[func_name]

        #print(f'LEAVE: FUNCTION {func_name}')
        #print(str(self.call_stack))

        self.call_stack.pop()

        return rv

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
        if op == TokenType.MOD:
            return lhs % rhs
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
        elif op == TokenType.NOT:
            return not self.visit(node.operand)

    def visit_NoOp(self, node):
        pass

    def visit_IFStatement(self, node):
        if (self.visit(node.expr)):
            self.visit(node.statement)
        else:
            self.visit(node.else_statement)

    def visit_CaseStatement(self, node: CaseStatement):
        case_value = self.visit(node.expr)
        for labels, statement in node.branches:
            for label in labels:
                if case_value == self.visit(label):
                    self.visit(statement)
                    return
        self.visit(node.else_statement)

    def visit_WhileStatement(self, node):
        while(self.visit(node.expr)):
            self.visit(node.statement)

    def visit_RepeatUntilStatement(self, node: RepeatUntilStatement):
        while True:
            for statement in node.statements:
                self.visit(statement)
            if self.visit(node.expr):
                break

    def visit_ForStatement(self, node: ForStatement):
        var_name = node.id.value
        val_init = self.visit(node.expr1)
        ar = self.call_stack.peek()
        ar.assign_existing(var_name, val_init)
        val_final = self.visit(node.expr2)
        if node.dir.type == TokenType.TO:
            while ar.get(var_name) <= val_final:
                self.visit(node.statement)
                ar.assign_existing(var_name, ar.get(var_name) + 1)
        else:
            while ar.get(var_name) >= val_final:
                self.visit(node.statement)
                ar.assign_existing(var_name, ar.get(var_name) - 1)
