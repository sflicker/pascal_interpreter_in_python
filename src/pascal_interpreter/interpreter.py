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
import math
import sys
from pathlib import Path

from .CallStack import CallStack
from .activation_record import ActivationRecord, ARType
from .data_type import DataType
from .error_code import ErrorCode, PascalRuntimeError
from .symbol import BuiltinFunctionSymbol, BuiltinProcedureSymbol
from .tokenizer import TokenType

#from pascal_parser import Parser
#from pascal_symbol import SymbolTableBuilder
from .pascal_ast import NodeVisitor, Program, Block, Assign, ProcedureCall, FunctionCall, \
    VariableDeclaration, LabelStatement, GotoStatement, ForStatement, RepeatUntilStatement, CaseStatement
from .pascal_ast import Ident, IndexedVariable, FieldVariable, RecordType, ArrayType, WithStatement
from .debugger import DebuggerQuit


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


class PascalFile:
    def __init__(self, base_dir=None):
        self.path = None
        self.resolved_path = None
        self.handle = None
        self.mode = None
        self.input = None
        self.base_dir = Path(base_dir) if base_dir is not None else None

    def assign(self, path):
        self.path = path
        file_path = Path(path)
        if self.base_dir is not None and not file_path.is_absolute():
            file_path = self.base_dir / file_path
        self.resolved_path = file_path

    def reset(self):
        self.close()
        self.handle = open(self.resolved_path, "r")
        self.mode = "r"
        self.input = PascalInput(self.handle)

    def rewrite(self):
        self.close()
        self.resolved_path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = open(self.resolved_path, "w")
        self.mode = "w"
        self.input = None

    def close(self):
        if self.handle is not None:
            self.handle.close()
        self.handle = None
        self.mode = None
        self.input = None

    def __eq__(self, other):
        if other is None:
            return self.path is None and self.handle is None
        if isinstance(other, dict):
            return other == {
                "path": self.path,
                "mode": self.mode,
                "open": self.handle is not None,
            }
        return False

    def __repr__(self):
        return str({
            "path": self.path,
            "mode": self.mode,
            "open": self.handle is not None,
        })


class PascalArray(dict):
    def __init__(self, lower=None, upper=None, component_type=None, dimension=0):
        super().__init__()
        self.lower = lower
        self.upper = upper
        self.component_type = component_type
        self.dimension = dimension

    def check_index(self, index):
        if self.lower is None or self.upper is None:
            return
        if index < self.lower or index > self.upper:
            raise PascalRuntimeError(
                error_code=ErrorCode.RUNTIME_ERROR,
                message=f"Array index {index} outside bounds {self.lower}..{self.upper}",
            )

    def set(self, index, value):
        self.check_index(index)
        self[str(index)] = value

    def get_index(self, index):
        self.check_index(index)
        return self.get(str(index))

    def get_or_create_index(self, index):
        self.check_index(index)
        key = str(index)
        if key not in self:
            self[key] = array_value_for_type(self.component_type, self.dimension + 1)
        return self[key]


def array_bounds(index_type):
    lower = upper = None
    if hasattr(index_type, "lower"):
        lower = index_type.lower.value
        upper = index_type.upper.value
    return lower, upper


def array_value_for_type(type_node, dimension=0):
    if isinstance(type_node, ArrayType):
        index_type = type_node.indexTypes[dimension]
        lower, upper = array_bounds(index_type)
        return PascalArray(lower, upper, type_node, dimension)
    return None


class Interpreter(NodeVisitor):
    def __init__(self, tree, *, interactive_input=False, debugger=None, file_base_dir=None):
        self.tree = tree
        self.call_stack = CallStack()
        self.interactive_input = interactive_input
        self.debugger = debugger
        self.input = PascalInput(sys.stdin)
        self.file_base_dir = file_base_dir

    def interpret(self):
        self.output = io.StringIO()
        tree = self.tree
        if tree is None:
            return ''
        quit_requested = False
        try:
            rv = self.visit(self.tree)
        except DebuggerQuit:
            quit_requested = True
            rv = self.call_stack.peek() if self.call_stack._records else None

        if self.debugger is not None and not quit_requested:
            self.debugger.program_finished(rv)

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
                ar.set_new(decl.name, self.initial_value(decl.type), decl.type.data_type, self.declaration_bounds(decl))

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
        ar.set_new(node.name, self.initial_value(node.type), node.type.data_type, self.declaration_bounds(node))

    def initial_value(self, type_node):
        if isinstance(type_node, ArrayType):
            lower, upper = array_bounds(type_node.indexType)
            return PascalArray(lower, upper, type_node)
        if isinstance(type_node, RecordType):
            return {
                field.name: self.initial_value(field.type)
                for field in type_node.fields
            }
        if type_node.data_type == DataType.TEXT:
            return PascalFile(self.file_base_dir)
        return None

    def declaration_bounds(self, declaration):
        if hasattr(declaration.type, "lower"):
            return (declaration.type.lower.value, declaration.type.upper.value)
        return None

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

    def before_statement(self, node):
        if self.debugger is not None:
            self.debugger.before_statement(node, self.call_stack)

    def visit_Assign(self, node: Assign):
        self.before_statement(node)
        val = self.visit(node.rhs)
        self.assign_variable(node.lhs, val)

    def assign_variable(self, variable, val):
        ar = self.call_stack.peek()
        if isinstance(variable, FieldVariable):
            record_value = self.visit(variable.record)
            record_value[variable.field_name.value] = val
        elif hasattr(variable, "index_expression"):
            array_name = variable.name.value
            array_value = ar.get(array_name)
            indexes = [self.visit(expr) for expr in variable.index_expressions]
            for index in indexes[:-1]:
                array_value = array_value.get_or_create_index(index)
            array_value.set(indexes[-1], val)
        else:
            ar.assign_existing(variable.value, val)

    def visit_LabelStatement(self, node: LabelStatement):
        self.before_statement(node)
        self.visit(node.statement)

    def visit_GotoStatement(self, node: GotoStatement):
        self.before_statement(node)
        raise GotoSignal(node.label)

    def visit_Ident(self, node):
        var_name = node.value

        ar = self.call_stack.peek()
        var_value = ar.get(var_name)

        return var_value

    def visit_IndexedVariable(self, node):
        ar = self.call_stack.peek()
        array_value = ar.get(node.name.value)
        indexes = [self.visit(expr) for expr in node.index_expressions]
        for index in indexes[:-1]:
            array_value = array_value.get_or_create_index(index)
        return array_value.get_index(indexes[-1])

    def visit_FieldVariable(self, node):
        record_value = self.visit(node.record)
        return record_value.get(node.field_name.value)

    def visit_Output(self, node):
        self.before_statement(node)

        l = []
        arguments = node.arguments
        output_target = self.output
        if arguments and self.is_text_file_variable(arguments[0]):
            output_target = self.visit(arguments[0]).handle
            arguments = arguments[1:]

        if arguments != None:
            for arg in arguments:
                l.append(str(self.visit(arg)))

        if node.op.value == "WRITELN":
            outstr = "".join(l)
            output_target.write(outstr)
            output_target.write('\n')
        elif node.op.value == "WRITE":
            output_target.write("".join(l))

        if self.debugger is not None and self.output.getvalue():
            print(self.output.getvalue(), end='', flush=True)
            self.debugger.notify_program_output()
            self.output = io.StringIO()

    def visit_Input(self, node):
        self.before_statement(node)
        if self.interactive_input:
            print(self.output.getvalue(), end='', flush=True)
            self.output = io.StringIO()

        arguments = node.arguments
        input_source = self.input
        if arguments and self.is_text_file_variable(arguments[0]):
            input_source = self.visit(arguments[0]).input
            arguments = arguments[1:]

        for arg in arguments:
            self.assign_variable(arg, self.convert_input(input_source.read_token(), self.variable_type(arg)))

        if node.op.value == "READLN":
            input_source.discard_line()

    def variable_type(self, variable):
        if isinstance(variable, FieldVariable):
            return variable.field_declaration.type.data_type
        if hasattr(variable, "index_expressions"):
            return variable.component_type
        return self.call_stack.peek().get_type(variable.value)

    def is_text_file_variable(self, node):
        if not isinstance(node, (Ident, IndexedVariable, FieldVariable)):
            return False
        return self.variable_type(node) is DataType.TEXT

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

    def visit_EnumConstant(self, node):
        return node.value

    def visit_ProcedureCall(self, node: ProcedureCall):
        self.before_statement(node)
        proc_name = node.proc_name
        proc_symbol = node.proc_symbol

        if isinstance(proc_symbol, BuiltinProcedureSymbol):
            if proc_name == "ASSIGN":
                self.visit(node.actual_params[0]).assign(self.visit(node.actual_params[1]))
            elif proc_name == "RESET":
                self.visit(node.actual_params[0]).reset()
            elif proc_name == "REWRITE":
                self.visit(node.actual_params[0]).rewrite()
            elif proc_name == "CLOSE":
                self.visit(node.actual_params[0]).close()
            return

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
            if param_symbol.by_reference:
                target_ar = self.call_stack.peek().find_record_containing(argument_node.value)
                ar.set_reference(param_symbol.name, target_ar, argument_node.value, param_symbol.type)
            else:
                ar.set_new(param_symbol.name, self.visit(argument_node), param_symbol.type)

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

        if isinstance(func_symbol, BuiltinFunctionSymbol):
            if func_name == "ABS":
                return abs(self.visit(node.actual_params[0]))
            if func_name == "SQR":
                value = self.visit(node.actual_params[0])
                return value * value
            if func_name == "ODD":
                return self.visit(node.actual_params[0]) % 2 != 0
            if func_name == "ORD":
                value = self.visit(node.actual_params[0])
                if isinstance(value, bool):
                    return int(value)
                if isinstance(value, str):
                    return ord(value[0])
                return value
            if func_name == "CHR":
                return chr(self.visit(node.actual_params[0]))
            if func_name == "PRED":
                value = self.visit(node.actual_params[0])
                if isinstance(value, str):
                    return chr(ord(value[0]) - 1)
                return value - 1
            if func_name == "SUCC":
                value = self.visit(node.actual_params[0])
                if isinstance(value, str):
                    return chr(ord(value[0]) + 1)
                return value + 1
            if func_name == "TRUNC":
                return math.trunc(self.visit(node.actual_params[0]))
            if func_name == "ROUND":
                value = self.visit(node.actual_params[0])
                if value >= 0:
                    return math.floor(value + 0.5)
                return math.ceil(value - 0.5)
            if func_name == "SQRT":
                return math.sqrt(self.visit(node.actual_params[0]))
            if func_name == "EXP":
                return math.exp(self.visit(node.actual_params[0]))
            if func_name == "LN":
                return math.log(self.visit(node.actual_params[0]))
            if func_name == "SIN":
                return math.sin(self.visit(node.actual_params[0]))
            if func_name == "COS":
                return math.cos(self.visit(node.actual_params[0]))
            if func_name == "ARCTAN":
                return math.atan(self.visit(node.actual_params[0]))

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
            if param_symbol.by_reference:
                target_ar = self.call_stack.peek().find_record_containing(argument_node.value)
                ar.set_reference(param_symbol.name, target_ar, argument_node.value, param_symbol.type)
            else:
                ar.set_new(param_symbol.name, self.visit(argument_node), param_symbol.type)
        # add a member with the function name for the return
        ar.set_new(func_name, None, func_symbol.return_type)

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
        self.before_statement(node)
        if (self.visit(node.expr)):
            self.visit(node.statement)
        else:
            self.visit(node.else_statement)

    def visit_CaseStatement(self, node: CaseStatement):
        self.before_statement(node)
        case_value = self.visit(node.expr)
        for labels, statement in node.branches:
            for label in labels:
                if case_value == self.visit(label):
                    self.visit(statement)
                    return
        self.visit(node.else_statement)

    def visit_WhileStatement(self, node):
        self.before_statement(node)
        while(self.visit(node.expr)):
            self.visit(node.statement)

    def visit_RepeatUntilStatement(self, node: RepeatUntilStatement):
        self.before_statement(node)
        while True:
            for statement in node.statements:
                self.visit(statement)
            if self.visit(node.expr):
                break

    def visit_ForStatement(self, node: ForStatement):
        self.before_statement(node)
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

    def visit_WithStatement(self, node: WithStatement):
        self.before_statement(node)
        self.visit(node.statement)
