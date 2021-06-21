from pascal_tokenizer import TokenType
from pascal_ast import AST
from pascal_token import Token


class Expression(AST):
    pass

class Var(Expression):
    def __init__(self, token: Token) -> None:
        super().__init__()
        self.token: Token = token
        self.value: str = token.value


class Type(AST):
    def __init__(self, token: Token) -> None:
        super().__init__()
        self.token = token
        self.value = token.value

class Param(AST):
    def __init__(self, var_node, type_node) -> None:
        self.var_node = var_node
        self.type_node = type_node

class Block(AST):
    def __init__(self, declarations, compound_statement) -> None:
        super().__init__()
        self.declarations = declarations
        self.compound_statement = compound_statement


class Program(AST):
    def __init__(self, name: str, block: Block) -> None:
        super().__init__()
        self.name: str = name
        self.block: Block = block


class Declaration(AST):
    pass


class ProcedureDeclaration(Declaration):
    def __init__(self, proc_name: str, params, block: Block) -> None:
        super().__init__()
        self.proc_name: str = proc_name
        self.params = params
        self.block_node: Block = block


class VariableDeclaration(Declaration):
    def __init__(self, var_node: Var, type_node: Type) -> None:
        super().__init__()
        self.var_node: Var = var_node
        self.type_node: Type = type_node


class Num(Expression):
    def __init__(self, token) -> None:
        self.token = token
        self.number = token.value


class String(Expression):
    def __init__(self, value) -> None:
        self.value = value


class BinaryOp(Expression):
    def __init__(self, lhs: AST, op: Token, rhs: AST) -> None:
        self.op: Token = op
        self.token: Token = op
        self.lhs: AST = lhs
        self.rhs: AST = rhs


class UnaryOp(Expression):
    def __init__(self, op: Token, operand: AST) -> None:
        self.op: Token = op
        self.operand: AST = operand

class Statement(AST):
    pass


class Compound(Statement):
    """Represents a 'BEGIN ... END' block"""

    def __init__(self) -> None:
        super().__init__()
        self.children = []


class Output(Statement):
    def __init__(self, op: Token, arguments) -> None:
        super().__init__()
        self.op: Token = op
        self.arguments = arguments


class Input(Statement):
    def __init__(self, op: Token, arguments) -> None:
        super().__init__()
        self.op: Token = op
        self.arguments = arguments


class Assign(Statement):
    def __init__(self, lhs: AST, op: Token, rhs: AST) -> None:
        super().__init__()
        self.lhs: AST = lhs
        self.op: Token = op
        self.token: Token = op
        self.rhs: AST = rhs


class IFStatement(Statement):
    def __init__(self, expr, statement, else_statement) -> None:
        super().__init__()
        self.expr = expr
        self.statement = statement
        self.else_statement = else_statement


class WhileStatement(Statement):
    def __init__(self, expr, statement) -> None:
        super().__init__()
        self.expr = expr
        self.statement = statement


class NoOp(AST):
    def __init(self) -> None:
        pass


class Parser(object):
    """Parser accepts a list of tokens and returns an abstract syntax tree"""

    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.token_pos = 0
        self.current_token = self.tokens[self.token_pos]
        self.MultiOperator = [TokenType.MUL, TokenType.REAL_DIV, TokenType.INTEGER_DIV, TokenType.AND]
        self.AddOperator = [TokenType.PLUS, TokenType.MINUS, TokenType.OR]
        self.RelationOperator = [TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL,
                                 TokenType.LESS, TokenType.LESS_EQUAL]

    def parse(self):
        """
        program : PROGRAM variable [program_parameters] SEMI block DOT

        program_parameters : LPAREN ident_list RPAREN | empty

        ident_list : ID [COMMA ID]* | empty

        block : declarations compound_statement

        declarations : VAR [variable_declaration SEMI]+
                       | [PROCEDURE ID [LPAREN formal_parameter_list RPAREN] SEMI block SEMI]*
                       | empty

        variable_declaration : ID [COMMA ID]* COLON type_spec

        type_spec : INTEGER | REAL | STRING

        compound_statement: BEGIN statement_list END

        statement_list: statement | statement SEMI statement_list

        statement : compound_statement
                        | assignment_statement
                        | input_statement
                        | output_statement
                        | if_statement
                        | while_statement
                        | empty

        assignment_statement : variable ASSIGN expr

        if_statement: IF expression THEN statement [ELSE statement]

        while_statement: WHILE expression DO statement

        output_statement : WRITELN LPAREN exprList RPAREN

        input_statement : READLN LPAREN exprList RPAREN

        variable: ID

        expr_list: expr [LPAREN COMMA expr RPAREN]*

        expr : simple_expr [RELATION simple_expr]*

        simple_expr : term [[PLUS | MINUS] term]*

        term : factor [[MUL | INTEGER_DIV | FLOAT_DIV] factor]*

        factor : PLUS factor
                    | MINUS factor
                    | INTEGER_CONST
                    | REAL_CONST
                    | STRING_CONST
                    | LPAREN expr RPAREN
                    | variable
        """

        root = self.program()
        if self.current_token.type != TokenType.EOF:
            raise Exception("Parse Exception")
        return root

    def program(self):
        """program : PROGRAM variable [program_parameters] SEMI block DOT"""
        self.__eat_token(TokenType.PROGRAM)
        var_node = self.variable()
        prog_name = var_node.value
        self.program_parameters()  # for backward compatibility, just ignore
        self.__eat_token(TokenType.SEMI)
        block_node = self.block()
        program_node = Program(prog_name, block_node)
        self.__eat_token(TokenType.DOT)
        return program_node

    def program_parameters(self):
        """program_parameters : LPAREN ident_list RPAREN
                            | empty"""
        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)
            node = self.ident_list()
            self.__eat_token(TokenType.RPAREN)
            return node

        return None

    def ident_list(self):
        """ident_list : IDENT [COMMA IDENT]*
                    | empty
        """
        if self.current_token.type == TokenType.ID:
            root = self.variable()
            result = [root]
            while self.current_token.type == TokenType.COMMA:
                self.__eat_token(TokenType.COMMA)
                result.append(self.variable())

        return result

    def block(self):
        """block : declarations compound_statement"""
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes, compound_statement_node)
        return node

    def declarations(self) -> list[Declaration]:
        """declarations : [variable_declarations]
                          [procedure_declarations]
        variable_declarations : VAR [variable_declaration SEMI]+
        procedure_declarations : [PROCEDURE ID [LPAREN formal_parameter_list RPAREN] SEMI block SEMI]*
        """
        declarations = []

        if self.current_token.type == TokenType.VAR:
            self.__eat_token(TokenType.VAR)
            while self.current_token.type == TokenType.ID:
                variable_declarations = self.variable_declarations()
                self.__eat_token(TokenType.SEMI)
                declarations.extend(variable_declarations)

        while self.current_token.type == TokenType.PROCEDURE:
            self.__eat_token(TokenType.PROCEDURE)
            proc_name = self.current_token.value
            self.__eat_token(TokenType.ID)
            params = []

            if self.current_token.type == TokenType.LPAREN:
                self.__eat_token(TokenType.LPAREN)

                params = self.formal_parameter_list()

                self.__eat_token(TokenType.RPAREN)

            self.__eat_token(TokenType.SEMI)
            block_node = self.block()
            procedure_declaration = ProcedureDeclaration(proc_name, params, block_node)
            self.__eat_token(TokenType.SEMI)
            declarations.append(procedure_declaration)

        return declarations

    def formal_parameter_list(self):

        if not self.current_token.type == TokenType.ID:
            return []

        param_nodes = self.format_parameters()

        while self.current_token.type == TokenType.SEMI:
            self.__eat_token(TokenType.SEMI)
            param_nodes.extend(self.format_parameters())

        return param_nodes

    def format_parameters(self):
        """format_parameters : ID (COMMA ID) * COLON type_spec"""
        param_nodes = []

        param_tokens = [self.current_token]
        self.__eat_token(TokenType.ID)
        while self.current_token.type == TokenType.COMMA:
            self.__eat_token(TokenType.COMMA)
            param_tokens.append(self.current_token)
            self.__eat_token(TokenType.ID)

        self.__eat_token(TokenType.COLON)
        type_node = self.type_spec()

        for param_token in param_tokens:
            param_node = Param(Var(param_token), type_node)
            param_nodes.append(param_node)

        return param_nodes


    def variable_declarations(self) -> list[VariableDeclaration]:
        """variable_declaration : ID [COMMA ID]* COLON type_spec"""
        var_nodes = [Var(self.current_token)]  # first ID
        self.__eat_token(TokenType.ID)

        while self.current_token.type == TokenType.COMMA:
            self.__eat_token(TokenType.COMMA)
            var_nodes.append(Var(self.current_token))
            self.__eat_token(TokenType.ID)

        self.__eat_token(TokenType.COLON)

        type_node = self.type_spec()
        var_declarations = [VariableDeclaration(var_node, type_node) for var_node in var_nodes]
        return var_declarations

    def type_spec(self):
        """type_spec : INTEGER | REAL | STRING"""
        token = self.current_token
        if self.current_token.type == TokenType.INTEGER:
            self.__eat_token(TokenType.INTEGER)
        elif self.current_token.type == TokenType.REAL:
            self.__eat_token(TokenType.REAL)
        elif self.current_token.type == TokenType.STRING:
            self.__eat_token(TokenType.STRING)
        else:
            raise Exception("Unknown Type - " + self.current_token.value)
        node = Type(token)
        return node

    def compound_statement(self) -> Compound:
        """compound_statement: BEGIN statement_list END"""
        self.__eat_token(TokenType.BEGIN)
        nodes = self.statement_list()
        self.__eat_token(TokenType.END)

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self) -> list[Statement]:
        """statement_list: statement
                            | statement SEMI statement_list"""
        node = self.statement()
        results = [node]

        while self.current_token.type == TokenType.SEMI:
            self.__eat_token(TokenType.SEMI)
            results.append(self.statement())

        if self.current_token.type == TokenType.ID:
            raise Exception("Parse Exception")

        return results

    def statement(self) -> Statement:
        """statement : compound_statement
                        | assignment_statement
                        | input_statement
                        | output_statement
                        | if_statement
                        | while_statement
                        | empty"""
        if self.current_token.type == TokenType.BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == TokenType.ID:
            node = self.assignment_statement()
        elif self.current_token.type == TokenType.IF:
            node = self.if_statement()
        elif self.current_token.type == TokenType.INPUT:
            node = self.input_statement()
        elif self.current_token.type == TokenType.OUTPUT:
            node = self.output_statement()
        elif self.current_token.type == TokenType.WHILE:
            node = self.while_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self) -> Assign:
        """assignment_statement : variable ASSIGN expr"""
        lhs = self.variable()
        token = self.current_token
        self.__eat_token(TokenType.ASSIGN)
        rhs = self.expr()
        node = Assign(lhs, token, rhs)
        return node

    def if_statement(self) -> IFStatement:
        """if_statement: IF expression THEN statement [ELSE statement]"""
        self.__eat_token(TokenType.IF)
        expr = self.expr()
        self.__eat_token(TokenType.THEN)
        statement = self.statement()
        else_statement = None
        if self.current_token.type == TokenType.ELSE:
            self.__eat_token(TokenType.ELSE)
            else_statement = self.statement()
        return IFStatement(expr, statement, else_statement)

    def while_statement(self) -> WhileStatement:
        """while_statement: WHILE expression DO statement"""
        self.__eat_token(TokenType.WHILE)
        expr = self.expr()
        self.__eat_token(TokenType.DO)
        statement = self.statement()
        return WhileStatement(expr, statement)

    def output_statement(self) -> Output:
        """output_statement : WRITELN LPAREN exprList RPAREN"""
        token = self.current_token
        self.__eat_token(TokenType.OUTPUT)
        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)
            arguments = self.expr_list()
            self.__eat_token(TokenType.RPAREN)
            return Output(token, arguments)
        return Output(token, None)

    def input_statement(self) -> Input:
        """input_statement : READLN LPAREN exprList RPAREN"""
        token = self.current_token
        self.__eat_token(TokenType.INPUT)
        self.__eat_token(TokenType.LPAREN)
        arguments = self.expr_list()
        self.__eat_token(TokenType.RPAREN)
        return Input(token, arguments)

    def variable(self) -> Var:
        """variable: ID"""
        node = Var(self.current_token)
        self.__eat_token(TokenType.ID)
        return node

    def empty(self) -> AST:
        """an empty production"""
        return NoOp()

    def expr_list(self) -> list[AST]:
        """expr_list: expr [LPAREN COMMA expr RPAREN]*"""
        node = self.expr()
        result = [node]
        while self.current_token.type == TokenType.COMMA:
            self.__eat_token(TokenType.COMMA)
            result.append(self.expr())

        return result

    def expr(self) -> Expression:
        """expr : simple_expr [RELATION simple_expr]*"""
        root = self.simple_expr()
        while self.current_token.type in self.RelationOperator:
            lhs = root
            op = self.current_token
            self.__eat_token(op.type)
            rhs = self.simple_expr()
            root = BinaryOp(lhs, op, rhs)
        return root

    def simple_expr(self) -> Expression:
        """simple_expr : term ((PLUS | MINUS) term)*"""
        root = self.term()
        while self.current_token.type in self.AddOperator:
            lhs = root
            op = self.current_token
            self.__eat_token(op.type)

            rhs = self.term()

            root = BinaryOp(lhs, op, rhs)
        return root

    def term(self) -> Expression:
        """term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)*"""
        root = self.factor()

        while self.current_token.type in self.MultiOperator:
            lhs = root
            op = self.current_token
            self.__eat_token(op.type)

            rhs = self.factor()
            root = BinaryOp(lhs, op, rhs)

        return root

    def factor(self) -> Expression:
        """factor : PLUS factor
                    | MINUS factor
                    | INTEGER_CONST
                    | REAL_CONST
                    | STRING_CONST
                    | LPAREN expr RPAREN
                    | variable
        """
        token = self.current_token

        if token.type == TokenType.PLUS:
            self.__eat_token(TokenType.PLUS)
            return UnaryOp(token, self.factor())

        if token.type == TokenType.MINUS:
            self.__eat_token(TokenType.MINUS)
            return UnaryOp(token, self.factor())

        if token.type == TokenType.INTEGER_CONST:
            self.__eat_token(TokenType.INTEGER_CONST)
            return Num(token)

        if token.type == TokenType.REAL_CONST:
            self.__eat_token(TokenType.REAL_CONST)
            return Num(token)

        if token.type == TokenType.STRING_CONST:
            self.__eat_token(TokenType.STRING_CONST)
            return String(token)

        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)
            node = self.expr()
            self.__eat_token(TokenType.RPAREN)
            return node

        else:
            node = self.variable()
            return node

    def __advance_token(self) -> None:
        if self.current_token.type != TokenType.EOF:
            self.token_pos = self.token_pos + 1
            self.current_token = self.tokens[self.token_pos]

    def __eat_token(self, token_type: TokenType) -> None:
        if self.current_token.type == token_type:
            self.__advance_token()
        else:
            raise Exception("Parse Exception - Expected Type", token_type, ", Found", self.current_token.type)
