
#####################
## AST
#####################
from data_type import DataType
from token_type import Token

class AST(object):
    def __init__(self):
        pass

    def accept(self, visitor: "NodeVisitor"):
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

class Ident(Expression):
    def __init__(self, token: Token, value: str) -> None:
        super().__init__()
        self.token: Token = token
        self.value: str = value

#    def accept(self, visitor: NodeVisitor):
#        visitor.visit(self)

    def __repr__(self):
        return f'Identifier name={self.value}'


class Type(AST):
    def __init__(self, token: Token, data_type: DataType) -> None:
        super().__init__()
        self.data_type = data_type
        self.token = token
        # self.value = token.value

#    def accept(self, visitor: NodeVisitor):
#        visitor.visit(self)

class Param(AST):
    def __init__(self, name: str, type: Type) -> None:
        self.name = name
        self.type = type

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
        for declaration in self.declarations:
            declaration.accept(visitor)
        self.compound_statement.accept(visitor)
        super().accept(visitor)

class Program(AST):
    def __init__(self, name: str, block: Block) -> None:
        super().__init__()
        self.name: str = name
        self.block: Block = block

    def accept(self, visitor: NodeVisitor):
        # visitor.visit(self.block)
        super().accept(visitor)
        self.block.accept(visitor)

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

class FunctionDeclaration(Declaration):
    def __init__(self, func_name: str, params, return_type: Type, block: Block) -> None:
        super().__init__()
        self.func_name: str = func_name
        self.params = params
        self.return_type = return_type
        self.block_node: Block = block

    def accept(self, visitor: NodeVisitor):
        # visitor.visit(self.params)
        # visitor.visit(self.block_node)
        self.params.accept(visitor)
        self.block_node.accept(visitor)
        visitor.visit(self)

class VariableDeclaration(Declaration):
    def __init__(self, name: str, type: Type) -> None:
        super().__init__()
        self.name: str = name
        self.type: Type = type

    def accept(self, visitor: NodeVisitor):
        # self.name.accept(visitor)
        # self.type.accept(visitor)
        super().accept(visitor)
#        visitor.visit(self.var_node)
#        visitor.visit(self.type_node)
#        visitor.visit(self)

class ArrayDeclaration(Declaration):
    def __init__(self, name, startIndex, endIndex, type: Type) -> None:
        super().__init__()
        self.name: str = name
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.type = type

class Constant(Expression):
    def __init__(self, token: Token, value, type: Type):
        self.token = token
        self.value = value
        self.type = type

class ConstantDeclaration(Declaration):
    def __init__(self, name: str, const: Constant):
        self.name = name
        self.const = const

class IntegerConstant(Constant):
    def __init__(self, token: Token) -> None:
        super().__init__(token, token.value, Type(token, DataType.INTEGER))

#    def accept(self, visitor: NodeVisitor):
#        visitor.visit(self)

    def __repr__(self):
        return f'Integer={self.value}'

class RealConstant(Constant):
    def __init__(self, token: Token) -> None:
        super().__init__(token, token.value, Type(token, DataType.REAL))

#    def accept(self, visitor: NodeVisitor):
#        visitor.visit(self)

    def __repr__(self):
        return f'Real={self.value}'


class StringConstant(Constant):
    def __init__(self, token: Token) -> None:
        super().__init__(token, token.value, Type(token, DataType.STRING))

    # def accept(self, visitor: NodeVisitor):
    #     visitor.visit(self)

    def __repr__(self):
        return f'String=${self.value}'

class BooleanConstant(Constant):
    def __init__(self, token: Token):
        super().__init__(token, token.value, Type(token, DataType.BOOLEAN))

    def __repr__(self):
        return f'Boolean=${self.value}'

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

    def __repr__(self):
        return f'${self.lhs} ${self.op} ${self.rhs}'

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
        super().accept(visitor)

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
    def __init__(self, lhs: Ident, op: Token, rhs: Expression) -> None:
        super().__init__()
        self.lhs: Ident = lhs
        self.op: Token = op
        self.token: Token = op
        self.rhs: Expression = rhs

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
        super().accept(visitor)

class WhileStatement(Statement):
    def __init__(self, expr, statement) -> None:
        super().__init__()
        self.expr = expr
        self.statement = statement

    def accept(self, visitor: NodeVisitor):
        super().accept(visitor)

class ForStatement(Statement):
    def __init__(self, id, expr1, dir, expr2, statement):
        super().__init__()
        self.id = id
        self.expr1 = expr1
        self.dir = dir
        self.expr2 = expr2
        self.statement = statement

class ProcedureCall(AST):
    def __init__(self, proc_name, actual_params, token):
        self.proc_name = proc_name
        self.actual_params = actual_params
        self.token = token

        # a reference to procedure declaration symbol
        self.proc_symbol = None

class FunctionCall(Expression):
    def __init__(self, func_name, actual_params, token):
        self.func_name = func_name
        self.actual_params = actual_params
        self.token = token

        self.return_type = None

        # a reference to procedure declaration symbol
        self.func_symbol = None


class NoOp(AST):
    def __init(self) -> None:
        pass

    # def accept(self, visitor: NodeVisitor):
    #     pass