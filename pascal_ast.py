
#####################
## AST
#####################
from ast import NodeVisitor
from pascal_token import Token

class AST(object):
    def __init__(self):
        pass

    def accept(self, visitor: NodeVisitor):
        visitor.visit(self)

#####################
## AST visitor
#####################

class NodeVisitor(object):
    def visit(self, node: AST):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: AST):
        pass
#        raise Exception('No visit_{} method'.format(type(node).__name__))



class Expression(AST):
    pass
#    def accept(self, visitor: NodeVisitor):
#        visitor.visit(self)

class Var(Expression):
    def __init__(self, token: Token) -> None:
        super().__init__()
        self.token: Token = token
        self.value: str = token.value

#    def accept(self, visitor: NodeVisitor):
#        visitor.visit(self)

class Type(AST):
    def __init__(self, token: Token) -> None:
        super().__init__()
        self.token = token
        self.value = token.value

#    def accept(self, visitor: NodeVisitor):
#        visitor.visit(self)

class Param(AST):
    def __init__(self, var_node, type_node) -> None:
        self.var_node = var_node
        self.type_node = type_node

#    def accept(self, visitor: NodeVisitor):
#        visitor.visit(self)

class Block(AST):
    def __init__(self, declarations, compound_statement) -> None:
        super().__init__()
        self.declarations = declarations
        self.compound_statement = compound_statement

    def accept(self, visitor: NodeVisitor):
        # visitor.visit(self.declarations)
        # visitor.visit(self.compound_statement)
        self.declarations.accept(visitor)
        self.compound_statement.accept(visitor)
        visitor.visit(self)

class Program(AST):
    def __init__(self, name: str, block: Block) -> None:
        super().__init__()
        self.name: str = name
        self.block: Block = block

    def accept(self, visitor: NodeVisitor):
        # visitor.visit(self.block)
        self.block.accept(visitor)
        visitor.visit(self)

class Declaration(AST):
    pass

    # def accept(self, visitor: NodeVisitor):
    #     visitor.visit(self)

class ProcedureDeclaration(Declaration):
    def __init__(self, proc_name: str, params, block: Block) -> None:
        super().__init__()
        self.proc_name: str = proc_name
        self.params = params
        self.block_node: Block = block

    def accept(self, visitor: NodeVisitor):
        # visitor.visit(self.params)
        # visitor.visit(self.block_node)
        self.params.accept(visitor)
        self.block_node.accept(visitor)
        visitor.visit(self)

class VariableDeclaration(Declaration):
    def __init__(self, var_node: Var, type_node: Type) -> None:
        super().__init__()
        self.var_node: Var = var_node
        self.type_node: Type = type_node

    def accept(self, visitor: NodeVisitor):
        visitor.visit(self.var_node)
        visitor.visit(self.type_node)
        visitor.visit(self)

class Num(Expression):
    def __init__(self, token) -> None:
        self.token = token
        self.number = token.value

#    def accept(self, visitor: NodeVisitor):
#        visitor.visit(self)

class String(Expression):
    def __init__(self, value) -> None:
        self.value = value

    # def accept(self, visitor: NodeVisitor):
    #     visitor.visit(self)

class BinaryOp(Expression):
    def __init__(self, lhs: AST, op: Token, rhs: AST) -> None:
        self.op: Token = op
        self.token: Token = op
        self.lhs: AST = lhs
        self.rhs: AST = rhs

    def accept(self, visitor: NodeVisitor):
        self.lhs.accept(visitor)
        self.rhs.accept(visitor)
        super().accept(visitor)
#        visitor.visit(self)

class UnaryOp(Expression):
    def __init__(self, op: Token, operand: AST) -> None:
        self.op: Token = op
        self.operand: AST = operand

    def accept(self, visitor: NodeVisitor):
        self.operand.accept(visitor)
        super().accept(visitor)
#        visitor.visit(self)

class Statement(AST):
    pass

    # def accept(self, visitor: NodeVisitor):
    #     visitor.visit(self)

class Compound(Statement):
    """Represents a 'BEGIN ... END' block"""

    def __init__(self) -> None:
        super().__init__()
        self.children = []

    def accept(self, visitor: NodeVisitor):
        for child in self.children:
            child.accept(visitor)
        visitor.visit(self)

class Output(Statement):
    def __init__(self, op: Token, arguments) -> None:
        super().__init__()
        self.op: Token = op
        self.arguments = arguments

    def accept(self, visitor: NodeVisitor):
        for argument in self.arguments:
            argument.accept(visitor)
        #visitor.visit(self)
        super().accept(visitor)

class Input(Statement):
    def __init__(self, op: Token, arguments) -> None:
        super().__init__()
        self.op: Token = op
        self.arguments = arguments

    def accept(self, visitor: NodeVisitor):
        for argument in self.arguments:
            argument.accept(visitor)
        #visitor.visit(self)
        super().accept(visitor)

class Assign(Statement):
    def __init__(self, lhs: AST, op: Token, rhs: AST) -> None:
        super().__init__()
        self.lhs: AST = lhs
        self.op: Token = op
        self.token: Token = op
        self.rhs: AST = rhs

    def accept(self, visitor: NodeVisitor):
        self.lhs.accept(visitor)
        self.rhs.accept(visitor)
#        visitor.visit(self)
        super().accept(visitor)

class IFStatement(Statement):
    def __init__(self, expr, statement, else_statement) -> None:
        super().__init__()
        self.expr = expr
        self.statement = statement
        self.else_statement = else_statement

    def accept(self, visitor: NodeVisitor):
        pass

class WhileStatement(Statement):
    def __init__(self, expr, statement) -> None:
        super().__init__()
        self.expr = expr
        self.statement = statement

    def accept(self, visitor: NodeVisitor):
        pass

class NoOp(AST):
    def __init(self) -> None:
        pass

    # def accept(self, visitor: NodeVisitor):
    #     pass