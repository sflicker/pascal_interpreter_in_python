from ast import NodeVisitor, AST
from token_type import TokenType


class SimpleInterpreter(NodeVisitor):
    """SimpleInterpreter - this version does not required variables to be declared so expressions and statements
        can be tested without a full pascal block."""
    def __init__(self, tree: AST):
        self.tree = tree
        self.GLOBAL_MEMORY = {}

    def interpret(self):
        tree = self.tree
        if tree is None:
            return ''
        return self.visit(self.tree)

    def visit_Ident(self, node):
        var_name = node.value
        if var_name not in self.GLOBAL_MEMORY.keys():
            self.GLOBAL_MEMORY[var_name] = None  # Since this is a simple interpreter declaration is not required.
        return self.GLOBAL_MEMORY.get(var_name)

    def visit_IntegerConstant(self, node):
        return node.value

    def visit_RealConstant(self, node):
        return node.value

    def visit_StringConstant(self, node):
        return node.value.value

    def visit_BooleanConstant(self, node):
        return node.value.value

    def visit_BinaryOp(self, node):
        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)
        op = node.token.type

        if op == TokenType.PLUS:
            return lhs + rhs
        elif op == TokenType.MINUS:
            return lhs - rhs
        elif op == TokenType.MUL:
            return lhs * rhs
        elif op == TokenType.REAL_DIV:
            return float(lhs / rhs)
        elif op == TokenType.INTEGER_DIV:
            return lhs // rhs
        elif op == TokenType.EQUAL:
            return lhs == rhs
        elif op == TokenType.NOT_EQUAL:
            return lhs != rhs
        elif op == TokenType.GREATER:
            return lhs > rhs
        elif op == TokenType.GREATER_EQUAL:
            return lhs >= rhs
        elif op == TokenType.LESS:
            return lhs < rhs
        elif op == TokenType.LESS_EQUAL:
            return lhs <= rhs
        elif op == TokenType.AND:
            return lhs and rhs
        elif op == TokenType.OR:
            return lhs or rhs

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op = node.op.type
        if op == TokenType.PLUS:
            return + operand
        elif op == TokenType.MINUS:
            return - operand

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        var_name = node.lhs.value
        var_value = self.visit(node.rhs)
        self.GLOBAL_MEMORY[var_name] = var_value

    def visit_IFStatement(self, node):
        if self.__expr_is_true(node.expr):
            self.visit(node.statement)
        elif node.else_statement is not None:
            self.visit(node.else_statement)

    def visit_WhileStatement(self, node):
        while self.__expr_is_true(node.expr):
            self.visit(node.statement)

    def __expr_is_true(self, expr):
        return self.visit(expr)
