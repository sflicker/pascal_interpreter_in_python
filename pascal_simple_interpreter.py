from pascal_ast import NodeVisitor, AST
from pascal_token import TokenType


class SimpleInterpreter(NodeVisitor):
    """SimpleInterpreter - this version does not required variables to be declared so expressions and statements
        can be tested without a full pascal block."""
    def __init__(self, tree: AST):
        self.tree = tree
        self.results = {}
        self.GLOBAL_MEMORY = {}

    def interpret(self):
        tree = self.tree
        if tree is None:
            return ''
        tree.accept(self)
        return self.results.get(self.tree)

    def visit_Var(self, node):
        var_name = node.value
        if var_name not in self.GLOBAL_MEMORY.keys():
            self.GLOBAL_MEMORY[var_name] = None  # Since this is a simple interpreter declaration is not required.
        self.results[node] = self.GLOBAL_MEMORY[var_name]

    def visit_Assign(self, node):
        var_name = node.lhs.value
        var_value = self.results[node.rhs]
        self.GLOBAL_MEMORY[var_name] = var_value

    def visit_Num(self, node):
        self.results[node] = node.number

    def visit_String(self, node):
        self.results[node] = node.value.value

    def visit_BinaryOp(self, node):
        lhs = self.results.get(node.lhs)
        rhs = self.results.get(node.rhs)
        op = node.token.type

        if op == TokenType.PLUS:
            self.results[node] = lhs + rhs
        elif op == TokenType.MINUS:
            self.results[node] = lhs - rhs
        elif op == TokenType.MUL:
            self.results[node] = lhs * rhs
        elif op == TokenType.REAL_DIV:
            self.results[node] = float(lhs / rhs)
        elif op == TokenType.INTEGER_DIV:
            self.results[node] = lhs // rhs
        elif op == TokenType.EQUAL:
            self.results[node] = lhs == rhs
        elif op == TokenType.NOT_EQUAL:
            self.results[node] = lhs != rhs
        elif op == TokenType.GREATER:
            self.results[node] = lhs > rhs
        elif op == TokenType.GREATER_EQUAL:
            self.results[node] = lhs >= rhs
        elif op == TokenType.LESS:
            self.results[node] = lhs < rhs
        elif op == TokenType.LESS_EQUAL:
            self.results[node] = lhs <= rhs
        elif op == TokenType.AND:
            self.results[node] = lhs and rhs
        elif op == TokenType.OR:
            self.results[node] = lhs or rhs

    def visit_UnaryOp(self, node):
        operand = self.results[node.operand]
        op = node.op.type
        if op == TokenType.PLUS:
            self.results[node] = + operand
        elif op == TokenType.MINUS:
            self.results[node] = - operand