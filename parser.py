from error_code import ParserError, ErrorCode
from symbol import ScopedSymbolTable, VarSymbol, ProcedureSymbol, FunctionSymbol, BuiltinIOSymbol
from tokenizer import TokenType
from pascal_interpreter.ast import AST, Program, Block, Declaration, ProcedureDeclaration, Param, Ident, VariableDeclaration, \
    Compound, Statement, Assign, IFStatement, WhileStatement, Output, Input, NoOp, Expression, BinaryOp, UnaryOp, Num, \
    String, Type, ProcedureCall, FunctionDeclaration, FunctionCall
from token_type import Token


class Parser(object):
    """Parser accepts a list of tokens and returns an abstract syntax tree"""

    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.token_pos = 0
        self.current_token = self.tokens[self.token_pos]

        self.current_scope: ScopedSymbolTable = None

        self.MultiOperator = [TokenType.MUL, TokenType.REAL_DIV, TokenType.INTEGER_DIV, TokenType.AND]
        self.AddOperator = [TokenType.PLUS, TokenType.MINUS, TokenType.OR]
        self.RelationOperator = [TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL,
                                 TokenType.LESS, TokenType.LESS_EQUAL]

    def error(self, error_code, token):
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )

    def parse(self):
        root = self.parse_program()
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, token=self.current_token, )
        return root

    def parse_expression(self):
        root = self.expr()
        if self.current_token.type != TokenType.EOF:
            raise Exception("Parse Exception")
        return root

    def parse_statement(self):
        root = self.statement()
        if self.current_token.type not in [TokenType.SEMI, TokenType.EOF]:
            raise Exception("Parse Exception")
        return root

    def parse_program(self):
        """
        program : PROGRAM variable [program_parameters] SEMI block DOT

        program_parameters : LPAREN ident_list RPAREN | empty

        ident_list : ID [COMMA ID]* | empty

        block : declarations compound_statement

        declarations : variable-declaration-part
                       | procedure-and-function-declaration-part
                       | empty

        variable-declaration-part : VAR variable_declaration+

        variable_declaration : ID [COMMA ID]* COLON type_spec SEMI

        procedure-and-function-declaration-part : procedure-declaration* |
                                                  function-declaration*

        procedure-declaration : PROCEDURE ID [LPAREN formal_parameter_list RPAREN] SEMI block SEMI

        function-declaration : FUNCTION ID [LPAREN formal_parameter_list RPAREN] COLON type SEMI block SEMI


        type_spec : INTEGER | REAL | STRING

        compound_statement: BEGIN statement_list END

        statement_list: statement | statement SEMI statement_list

        statement : compound_statement
                        | assignment_statement
                        | input_statement
                        | output_statement
                        | if_statement
                        | while_statement
                        | proccall_statement
                        | empty

        assignment_statement : variable ASSIGN expr

        if_statement: IF expression THEN statement [ELSE statement]

        while_statement: WHILE expression DO statement

        proccall_statement: ID LPAREN (expr (COMMA expr)*)? RPAREN

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

        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope
        )

        global_scope.init_builtins()
        self.current_scope = global_scope

        self.__eat_token(TokenType.PROGRAM)
        var_node = self.variable()
        prog_name = var_node.value
        self.program_parameters()  # for backward compatibility, just ignore
        self.__eat_token(TokenType.SEMI)
        block_node = self.block(None)  # currently ignoring program parameters.
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
        result = None
        if self.current_token.type == TokenType.ID:
            root = self.variable()
            result = [root]
            while self.current_token.type == TokenType.COMMA:
                self.__eat_token(TokenType.COMMA)
                result.append(self.variable())

        return result

    def block(self, params=None):
        """block : declarations compound_statement"""
        parent_scope = self.current_scope

        local_scope = ScopedSymbolTable(
            scope_name=f'block#{parent_scope.scope_level}',
            scope_level=parent_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )

        if params is not None:
            for param in params:
                local_scope.insert(VarSymbol(param.name, param.type))

        self.current_scope = local_scope

        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes, compound_statement_node)

        print(self.current_scope)
        self.current_scope = parent_scope
        return node

    def declarations(self) -> list[Declaration]:
        """declarations : [variable_declarations]
                          [procedure_declarations]
        variable_declarations : VAR [variable_declaration SEMI]+
        procedure_declarations : [PROCEDURE ID [LPAREN formal_parameter_list RPAREN] SEMI block SEMI]*
        function_declarations : [FUNCTION ID [LPAREN format_parameter_list RPAREN] COLON type SEMI block SEMI]*
        """
        declarations = []

        self.handle_var_declarations(declarations)

        self.handle_procedure_and_function_declarations(declarations)

        return declarations

    def handle_var_declarations(self, declarations: list):
        while self.current_token.type == TokenType.VAR:
            self.__eat_token(TokenType.VAR)
            while self.current_token.type == TokenType.ID:
                variable_declarations = self.variable_declarations()
                self.__eat_token(TokenType.SEMI)
                declarations.extend(variable_declarations)

    def handle_procedure_and_function_declarations(self, declarations: list):
        found = True
        while found:
            if self.current_token.type == TokenType.PROCEDURE:
                procedure_declaration = self.procedure_declaration()
                declarations.append(procedure_declaration)
            elif self.current_token.type == TokenType.FUNCTION:
                function_declaration = self.function_declaration()
                declarations.append(function_declaration)
            else:
                found = False

    def procedure_declaration(self):
        self.__eat_token(TokenType.PROCEDURE)
        proc_name = self.current_token.value
        self.__eat_token(TokenType.ID)

        params = None

        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)

            params = self.formal_parameter_list()

            self.__eat_token(TokenType.RPAREN)

        self.__eat_token(TokenType.SEMI)
        self.current_scope.insert(ProcedureSymbol(proc_name))
        block_node = self.block(params)
        procedure_declaration = ProcedureDeclaration(proc_name, params, block_node)
        self.__eat_token(TokenType.SEMI)
        return procedure_declaration

    def function_declaration(self):
        self.__eat_token(TokenType.FUNCTION)
        proc_name = self.current_token.value
        self.__eat_token(TokenType.ID)

        params = None

        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)

            params = self.formal_parameter_list()

            self.__eat_token(TokenType.RPAREN)

        self.__eat_token(TokenType.COLON)

        return_type = self.type_spec()

        self.__eat_token(TokenType.SEMI)

        self.current_scope.insert(FunctionSymbol(proc_name, return_type))

        return_param = Param(proc_name, return_type)

        combined_params = []
        if params is not None:
            combined_params.extend(params)
        combined_params.append(return_param)

        block_node = self.block(combined_params)
        procedure_declaration = FunctionDeclaration(proc_name, params, return_type, block_node)

        self.__eat_token(TokenType.SEMI)
        return procedure_declaration

    def formal_parameter_list(self):

        if not self.current_token.type == TokenType.ID:
            return []

        param_nodes = self.formal_parameters()

        while self.current_token.type == TokenType.SEMI:
            self.__eat_token(TokenType.SEMI)
            param_nodes.extend(self.formal_parameters())

        return param_nodes

    def formal_parameters(self):
        """formal_parameters : ID (COMMA ID) * COLON type_spec"""
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
            param_node = Param(param_token.value, type_node)
            param_nodes.append(param_node)

        return param_nodes

    def variable_declarations(self) -> list[VariableDeclaration]:
        """variable_declaration : ID [COMMA ID]* COLON type_spec"""
        var_nodes = [Ident(self.current_token.value)]  # first ID
        self.__eat_token(TokenType.ID)

        while self.current_token.type == TokenType.COMMA:
            self.__eat_token(TokenType.COMMA)
            var_nodes.append(Ident(self.current_token.value))
            self.__eat_token(TokenType.ID)

        self.__eat_token(TokenType.COLON)

        type_node = self.type_spec()
        var_declarations = [VariableDeclaration(var_node.value, type_node) for var_node in var_nodes]
        for declaration in var_declarations:
            self.current_scope.insert(VarSymbol(declaration.name, declaration.type))
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
                        | proccall_statement
                        | empty"""
        if self.current_token.type == TokenType.BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == TokenType.INPUT:
            node = self.input_statement()
        elif self.current_token.type == TokenType.ID and self.__is_io(self.current_token):
            node = self.output_statement()
        elif self.current_token.type == TokenType.ID and self.__is_procedure(self.current_token):
            node = self.proccall_statement()
        elif self.current_token.type == TokenType.ID and self.__is_variable(
                self.current_token) and self.__peek_next_token_type() == TokenType.ASSIGN:
            node = self.assignment_statement()
        elif self.current_token.type == TokenType.IF:
            node = self.if_statement()
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

    def proccall_statement(self):
        """proccall_statement: ID IPAREN (expr (COMMA expr)*)? RPAREN"""
        token = self.current_token

        proc_name = token.value

        self.__eat_token(TokenType.ID)
        actual_params = None

        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)

            actual_params = []

            if self.current_token.type != TokenType.RPAREN:
                node = self.expr()
                actual_params.append(node)

            while self.current_token.type == TokenType.COMMA:
                self.__eat_token(TokenType.COMMA)
                node = self.expr()
                actual_params.append(node)

            self.__eat_token(TokenType.RPAREN)

        node = ProcedureCall(
            proc_name=proc_name,
            actual_params=actual_params,
            token=token
        )

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
        self.__eat_token(TokenType.ID)
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

    def variable(self) -> Ident:
        """variable: ID"""
        node = Ident(self.current_token.value)
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

    def funccall_expression(self) -> Expression:
        token = self.current_token

        func_name = token.value

        self.__eat_token(TokenType.ID)
        actual_params = None

        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)

            actual_params = []

            if self.current_token.type != TokenType.RPAREN:
                node = self.expr()
                actual_params.append(node)

            while self.current_token.type == TokenType.COMMA:
                self.__eat_token(TokenType.COMMA)
                node = self.expr()
                actual_params.append(node)

            self.__eat_token(TokenType.RPAREN)

        node = FunctionCall(
            func_name=func_name,
            actual_params=actual_params,
            token=token
        )

        return node

    def factor(self) -> Expression:
        """factor : PLUS factor
                    | MINUS factor
                    | INTEGER_CONST
                    | REAL_CONST
                    | STRING_CONST
                    | LPAREN expr RPAREN
                    | ID [ LPAREN actual_params_list RPAREN]
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

        if self.current_token.type == TokenType.ID and self.__is_function(self.current_token):
            node = self.funccall_expression()
            return node

        if self.current_token.type == TokenType.ID and self.__is_variable(self.current_token):
            node = self.variable()
            return node

    def __advance_token(self) -> None:
        if self.current_token.type != TokenType.EOF:
            self.token_pos = self.token_pos + 1
            self.current_token = self.tokens[self.token_pos]

    def __peek_next_token_type(self):
        if self.current_token.type != TokenType.EOF:
            next_pos = self.token_pos + 1
            if next_pos > len(self.tokens) - 1:
                return None
            else:
                next_token = self.tokens[next_pos]
                return next_token.type

    def __eat_token(self, token_type: TokenType) -> None:
        if self.current_token.type == token_type:
            self.__advance_token()
        else:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )

    def __is_variable(self, token: Token) -> bool:
        if not token.type == TokenType.ID:
            self.error(error_code=ErrorCode.EXPECTED_IDENTIFIER, token=token)
        symbol = self.current_scope.lookup(token.value, False)
        if symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=token)
        return isinstance(symbol, VarSymbol)

    def __is_procedure(self, token: Token) -> bool:
        if not token.type == TokenType.ID:
            self.error(error_code=ErrorCode.EXPECTED_IDENTIFIER, token=token)
        symbol = self.current_scope.lookup(token.value, False)
        if symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=token)
        return isinstance(symbol, ProcedureSymbol)

    def __is_function(self, token: Token) -> bool:
        if not token.type == TokenType.ID:
            self.error(error_code=ErrorCode.EXPECTED_IDENTIFIER, token=token)
        symbol = self.current_scope.lookup(token.value, False)
        if symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=token)
        return isinstance(symbol, FunctionSymbol)

    def __is_io(self, token: Token) -> bool:
        if not token.type == TokenType.ID:
            self.error(error_code=ErrorCode.EXPECTED_IDENTIFIER, token=token)
        symbol = self.current_scope.lookup(token.value, False)
        if symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=token)
        return isinstance(symbol, BuiltinIOSymbol)
