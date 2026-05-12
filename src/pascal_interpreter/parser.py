from .error_code import ParserError, ErrorCode
from .data_type import DataType
from .symbol import ScopedSymbolTable, VarSymbol, ProcedureSymbol, FunctionSymbol, BuiltinIOSymbol, ConstSymbol, TypeSymbol
from .token_type import TokenType
from .pascal_ast import AST, Program, Block, Declaration, ProcedureDeclaration, Param, Ident, \
    VariableDeclaration, \
    Compound, Statement, Assign, LabelStatement, GotoStatement, IFStatement, CaseStatement, WhileStatement, Output, Input, NoOp, Expression, BinaryOp, \
    UnaryOp, \
    Type, ProcedureCall, FunctionDeclaration, FunctionCall, ForStatement, RepeatUntilStatement, Constant, IntegerConstant, \
    RealConstant, StringConstant, CharConstant, BooleanConstant, ConstantDeclaration, SubrangeType, ArrayType, RecordType, \
    SetType, PointerType, EnumType, EnumConstant, NilConstant, SetLiteral, IndexedVariable, FieldVariable, DereferenceVariable, OutputField, WithStatement
from .token_type import Token


class Parser(object):
    """Parser accepts a list of tokens and returns an abstract syntax tree"""

    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.token_pos = 0
        self.current_token = self.tokens[self.token_pos]
        self.current_routine = None

        self.current_scope: ScopedSymbolTable = None
        self.with_records = []
        self.forward_declarations = {}

        self.MultiOperator = [
            TokenType.MUL,
            TokenType.REAL_DIV,
            TokenType.INTEGER_DIV,
            TokenType.MOD,
            TokenType.AND,
        ]
        self.AddOperator = [TokenType.PLUS, TokenType.MINUS, TokenType.OR]
        self.RelationOperator = [TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL,
                                 TokenType.LESS, TokenType.LESS_EQUAL, TokenType.IN]

    def set_location(self, node, token):
        node.line = token.lineno
        node.column = token.column
        node.routine = self.current_routine
        return node

    def error(self, error_code, token):
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )

    def ensure_declaration_available(self, name, token, scope=None):
        scope = scope or self.current_scope
        if scope.lookup(name, current_scope_only=True):
            self.error(ErrorCode.DUPLICATE_ID, token)

    def insert_declaration(self, symbol, token, scope=None):
        scope = scope or self.current_scope
        self.ensure_declaration_available(symbol.name, token, scope)
        scope.insert(symbol)

    def forward_names(self, kind, scope=None):
        scope = scope or self.current_scope
        scope_forwards = self.forward_declarations.setdefault(id(scope), {"PROCEDURE": set(), "FUNCTION": set()})
        return scope_forwards[kind]

    def parse(self):
        root = self.parse_program()
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, token=self.current_token, )
        return root

    def parse_expression(self):
        root = self.expr()
        if self.current_token.type != TokenType.EOF:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
        return root

    def parse_statement(self):
        root = self.statement()
        if self.current_token.type not in [TokenType.SEMI, TokenType.EOF]:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
        return root

    def parse_program(self):
        """
        program : PROGRAM variable [program_parameters] SEMI block DOT

        program_parameters : LPAREN ident_list RPAREN | empty

        ident_list : ID [COMMA ID]* | empty

        block : declarations compound_statement

        declarations : [const-declaration-part]
                       [variable-declaration-part]
                       [procedure-and-function-declaration-part]

        const-declaration-part : const [ID EQUAL constant SEMI]+

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
                        | case_statement
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
                    | constant
                    | LPAREN expr RPAREN
                    | variable

        constant : INTEGER_CONST
                | REAL_CONST
                | STRING_CONST
        """

        root = self.program()
        if self.current_token.type != TokenType.EOF:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
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

        program_token = self.current_token
        self.__eat_token(TokenType.PROGRAM)
        var_node = self.identifier()
        prog_name = var_node.value
        parent_routine = self.current_routine
        self.current_routine = f"PROGRAM {prog_name}"
        self.program_parameters()  # for backward compatibility, just ignore
        self.__eat_token(TokenType.SEMI)
        block_node = self.block(None)  # currently ignoring program parameters.
        program_node = Program(prog_name, block_node)
        self.set_location(program_node, program_token)
        self.current_routine = parent_routine
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
            root = self.identifier()
            result = [root]
            while self.current_token.type == TokenType.COMMA:
                self.__eat_token(TokenType.COMMA)
                result.append(self.identifier())

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
                self.insert_declaration(
                    VarSymbol(param.name, param.type.data_type, param.by_reference, param.type),
                    param.type.token,
                    local_scope,
                )

        self.current_scope = local_scope

        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes, compound_statement_node)

        #print(self.current_scope)
        self.current_scope = parent_scope
        return node

    def declarations(self) -> list[Declaration]:
        """declarations : [constant_declarations]
                          [type-declarations]
                          [variable_declarations]
                          [procedure_declarations]
        variable_declarations : VAR [variable_declaration SEMI]+
        procedure_declarations : [PROCEDURE ID [LPAREN formal_parameter_list RPAREN] SEMI block SEMI]*
        function_declarations : [FUNCTION ID [LPAREN format_parameter_list RPAREN] COLON type SEMI block SEMI]*
        """
        declarations = []

        self.handle_label_declarations()

        self.handle_const_declarations(declarations)

        self.handle_type_declarations(declarations)

        self.handle_var_declarations(declarations)

        self.handle_procedure_and_function_declarations(declarations)

        return declarations

    def handle_label_declarations(self):
        if self.current_token.type == TokenType.LABEL:
            self.__eat_token(TokenType.LABEL)
            self.__eat_token(TokenType.INTEGER_CONST)
            while self.current_token.type == TokenType.COMMA:
                self.__eat_token(TokenType.COMMA)
                self.__eat_token(TokenType.INTEGER_CONST)
            self.__eat_token(TokenType.SEMI)

    def handle_const_declarations(self, declarations: list):
        if self.current_token.type == TokenType.CONST:
            const_declarations = []
            seen = set()
            self.__eat_token(TokenType.CONST)
            while self.current_token.type == TokenType.ID:
                const_declaration = self.const_declaration()
                self.__eat_token(TokenType.SEMI)
                if const_declaration.name in seen:
                    self.error(ErrorCode.DUPLICATE_ID, const_declaration.const.token)
                seen.add(const_declaration.name)
                const_declarations.append(const_declaration)
            for const_declaration in const_declarations:
                self.insert_declaration(
                    ConstSymbol(const_declaration.name, const_declaration.const),
                    const_declaration.const.token,
                )
            declarations.extend(const_declarations)

    def handle_type_declarations(self, declarations: list):
        if self.current_token.type == TokenType.TYPE:
            self.__eat_token(TokenType.TYPE)
            while self.current_token.type == TokenType.ID:
                type_declaration = self.type_declaration()
                self.__eat_token(TokenType.SEMI)
                self.insert_declaration(type_declaration, type_declaration.type_node.token)
                self.resolve_pointer_types()
                if isinstance(type_declaration.type_node, EnumType):
                    for enum_value in type_declaration.type_node.values:
                        self.insert_declaration(ConstSymbol(enum_value.name, enum_value), enum_value.token)

    def resolve_pointer_types(self):
        for symbol in self.current_scope._symbols.values():
            self.resolve_pointer_type_node(getattr(symbol, "type_node", None))

    def resolve_pointer_type_node(self, type_node):
        if isinstance(type_node, PointerType) and type_node.referenced_type is None:
            type_symbol = self.current_scope.lookup(type_node.referenced_name)
            if isinstance(type_symbol, TypeSymbol):
                type_node.referenced_type = type_symbol.type_node or Type(type_node.token, type_symbol.type)
        elif isinstance(type_node, RecordType):
            for field in type_node.fields:
                self.resolve_pointer_type_node(field.type)

    def type_declaration(self):
        identifier = Ident(self.current_token, self.current_token.value)
        self.__eat_token(TokenType.ID)
        self.__eat_token(TokenType.EQUAL)
        type_node = self.type_spec()
        return TypeSymbol(identifier.value, type_node.data_type, type_node)

    def handle_var_declarations(self, declarations: list):
        if self.current_token.type == TokenType.VAR:
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
        token = self.current_token
        self.__eat_token(TokenType.PROCEDURE)
        proc_name = self.current_token.value
        self.__eat_token(TokenType.ID)

        params = None

        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)

            params = self.formal_parameter_list()

            self.__eat_token(TokenType.RPAREN)

        self.__eat_token(TokenType.SEMI)
        if self.current_token.type == TokenType.FORWARD:
            self.__eat_token(TokenType.FORWARD)
            self.__eat_token(TokenType.SEMI)
            self.insert_declaration(ProcedureSymbol(proc_name), token)
            self.forward_names("PROCEDURE").add(proc_name)
            return ProcedureDeclaration(proc_name, params, None, forward=True)

        existing_symbol = self.current_scope.lookup(proc_name, current_scope_only=True)
        if isinstance(existing_symbol, ProcedureSymbol) and proc_name in self.forward_names("PROCEDURE"):
            self.forward_names("PROCEDURE").remove(proc_name)
        elif existing_symbol is not None:
            self.error(ErrorCode.DUPLICATE_ID, token)
        else:
            self.current_scope.insert(ProcedureSymbol(proc_name))
        parent_routine = self.current_routine
        self.current_routine = f"PROCEDURE {proc_name}"
        block_node = self.block(params)
        self.current_routine = parent_routine
        procedure_declaration = ProcedureDeclaration(proc_name, params, block_node)
        self.__eat_token(TokenType.SEMI)
        return procedure_declaration

    def function_declaration(self):
        token = self.current_token
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

        if self.current_token.type == TokenType.FORWARD:
            self.__eat_token(TokenType.FORWARD)
            self.__eat_token(TokenType.SEMI)
            self.insert_declaration(FunctionSymbol(proc_name, return_type.data_type), token)
            self.forward_names("FUNCTION").add(proc_name)
            return FunctionDeclaration(proc_name, params, return_type, None, forward=True)

        existing_symbol = self.current_scope.lookup(proc_name, current_scope_only=True)
        if isinstance(existing_symbol, FunctionSymbol) and proc_name in self.forward_names("FUNCTION"):
            self.forward_names("FUNCTION").remove(proc_name)
        elif existing_symbol is not None:
            self.error(ErrorCode.DUPLICATE_ID, token)
        else:
            self.current_scope.insert(FunctionSymbol(proc_name, return_type.data_type))

        return_param = Param(proc_name, return_type)

        combined_params = []
        if params is not None:
            combined_params.extend(params)
        combined_params.append(return_param)

        parent_routine = self.current_routine
        self.current_routine = f"FUNCTION {proc_name}"
        block_node = self.block(combined_params)
        self.current_routine = parent_routine
        procedure_declaration = FunctionDeclaration(proc_name, params, return_type, block_node)

        self.__eat_token(TokenType.SEMI)
        return procedure_declaration

    def formal_parameter_list(self):

        if self.current_token.type not in [TokenType.ID, TokenType.VAR]:
            return []

        param_nodes = self.formal_parameters()

        while self.current_token.type == TokenType.SEMI:
            self.__eat_token(TokenType.SEMI)
            param_nodes.extend(self.formal_parameters())

        return param_nodes

    def formal_parameters(self):
        """formal_parameters : [VAR] ID (COMMA ID) * COLON type_spec"""
        param_nodes = []
        by_reference = False

        if self.current_token.type == TokenType.VAR:
            by_reference = True
            self.__eat_token(TokenType.VAR)

        seen = set()
        param_tokens = [self.current_token]
        seen.add(self.current_token.value)
        self.__eat_token(TokenType.ID)
        while self.current_token.type == TokenType.COMMA:
            self.__eat_token(TokenType.COMMA)
            if self.current_token.value in seen:
                self.error(ErrorCode.DUPLICATE_ID, self.current_token)
            seen.add(self.current_token.value)
            param_tokens.append(self.current_token)
            self.__eat_token(TokenType.ID)

        self.__eat_token(TokenType.COLON)
        type_node = self.type_spec()

        for param_token in param_tokens:
            param_node = Param(param_token.value, type_node, by_reference)
            param_nodes.append(param_node)

        return param_nodes

    def const_declaration(self):
        """constant_declarations : ID EQUAL constant
           constant : REAL_CONSTANT | INTEGER_CONSTANT | STRING_CONSTANT
           """
        id = Ident(self.current_token, self.current_token.value)
        self.__eat_token(TokenType.ID)
        self.__eat_token(TokenType.EQUAL)
        const = self.get_constant()
        return ConstantDeclaration(id.value, const)


    def variable_declarations(self) -> list[VariableDeclaration]:
        """variable_declaration : ID [COMMA ID]* COLON type_spec"""
        var_nodes = [Ident(self.current_token, self.current_token.value)]  # first ID
        seen = {self.current_token.value}
        self.__eat_token(TokenType.ID)

        while self.current_token.type == TokenType.COMMA:
            self.__eat_token(TokenType.COMMA)
            if self.current_token.value in seen:
                self.error(ErrorCode.DUPLICATE_ID, self.current_token)
            seen.add(self.current_token.value)
            var_nodes.append(Ident(self.current_token, self.current_token.value))
            self.__eat_token(TokenType.ID)

        self.__eat_token(TokenType.COLON)

        type_node = self.type_spec()
        var_declarations = [VariableDeclaration(var_node.value, type_node) for var_node in var_nodes]
        for declaration in var_declarations:
            self.insert_declaration(
                VarSymbol(declaration.name, declaration.type.data_type, type_node=declaration.type),
                declaration.type.token,
            )
        return var_declarations

    def type_spec(self):
        """type_spec : INTEGER | REAL | STRING | CHAR | BOOLEAN"""
        token = self.current_token
        if token.type == TokenType.INTEGER:
            self.__eat_token(TokenType.INTEGER)
            node = Type(token, DataType.INTEGER)
        elif token.type == TokenType.REAL:
            self.__eat_token(TokenType.REAL)
            node = Type(token, DataType.REAL)
        elif token.type == TokenType.STRING:
            self.__eat_token(TokenType.STRING)
            node = Type(token, DataType.STRING)
        elif token.type == TokenType.CHAR:
            self.__eat_token(TokenType.CHAR)
            node = Type(token, DataType.CHAR)
        elif token.type == TokenType.BOOLEAN:
            self.__eat_token(TokenType.BOOLEAN)
            node = Type(token, DataType.BOOLEAN)
        elif token.type == TokenType.TEXT:
            self.__eat_token(TokenType.TEXT)
            node = Type(token, DataType.TEXT)
        elif token.type == TokenType.ARRAY:
            self.__eat_token(TokenType.ARRAY)
            self.__eat_token(TokenType.LEFT_BRACKET)
            indexTypes = [self.type_spec()]
            while self.current_token.type == TokenType.COMMA:
                self.__eat_token(TokenType.COMMA)
                indexTypes.append(self.type_spec())
            self.__eat_token(TokenType.RIGHT_BRACKET)
            self.__eat_token(TokenType.OF)
            componentType = self.type_spec()
            node = ArrayType(token, indexTypes[0], componentType, indexTypes)
        elif token.type == TokenType.SET:
            self.__eat_token(TokenType.SET)
            self.__eat_token(TokenType.OF)
            node = SetType(token, self.type_spec())
        elif token.type == TokenType.CARET:
            self.__eat_token(TokenType.CARET)
            referenced_name = self.current_token.value
            if self.current_token.type in [TokenType.ID, TokenType.INTEGER, TokenType.REAL, TokenType.STRING, TokenType.CHAR, TokenType.BOOLEAN]:
                if self.current_token.type == TokenType.ID:
                    self.__eat_token(TokenType.ID)
                else:
                    self.__eat_token(self.current_token.type)
                node = PointerType(token, referenced_name)
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
        elif token.type == TokenType.RECORD:
            node = self.record_type()
        elif token.type == TokenType.LPAREN:
            node = self.enum_type()
        elif self.__peek_next_token_type() == TokenType.DOTDOT:
            lower = self.get_constant()
            self.__eat_token(TokenType.DOTDOT)
            upper = self.get_constant()
            if lower.type.data_type != upper.type.data_type:
                self.error(ErrorCode.TYPE_ERROR, self.current_token)
            node = SubrangeType(token, lower, upper, lower.type.data_type)
        elif token.type == TokenType.ID:
            type_symbol = self.current_scope.lookup(token.value)
            if not isinstance(type_symbol, TypeSymbol):
                self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
            self.__eat_token(TokenType.ID)
            node = type_symbol.type_node or Type(token, type_symbol.type)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
#        node = Type(token)
        return node

    def record_type(self):
        """record_type : RECORD field_declaration* END"""
        token = self.current_token
        self.__eat_token(TokenType.RECORD)
        fields = []
        field_names = set()
        while self.current_token.type != TokenType.END:
            new_fields = self.field_declarations()
            for field in new_fields:
                if field.name in field_names:
                    self.error(ErrorCode.DUPLICATE_ID, field.type.token)
                field_names.add(field.name)
            fields.extend(new_fields)
            if self.current_token.type == TokenType.SEMI:
                self.__eat_token(TokenType.SEMI)
            elif self.current_token.type != TokenType.END:
                self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
        self.__eat_token(TokenType.END)
        return RecordType(token, fields)

    def enum_type(self):
        """enum_type : LPAREN ID (COMMA ID)* RPAREN"""
        token = self.current_token
        enum_type = EnumType(token)
        self.__eat_token(TokenType.LPAREN)
        ordinal = 0
        seen = set()
        self.ensure_declaration_available(self.current_token.value, self.current_token)
        seen.add(self.current_token.value)
        enum_type.values.append(EnumConstant(self.current_token, self.current_token.value, ordinal, enum_type))
        self.__eat_token(TokenType.ID)
        while self.current_token.type == TokenType.COMMA:
            self.__eat_token(TokenType.COMMA)
            ordinal += 1
            if self.current_token.value in seen:
                self.error(ErrorCode.DUPLICATE_ID, self.current_token)
            self.ensure_declaration_available(self.current_token.value, self.current_token)
            seen.add(self.current_token.value)
            enum_type.values.append(EnumConstant(self.current_token, self.current_token.value, ordinal, enum_type))
            self.__eat_token(TokenType.ID)
        self.__eat_token(TokenType.RPAREN)
        return enum_type

    def field_declarations(self):
        field_nodes = [Ident(self.current_token, self.current_token.value)]
        seen = {self.current_token.value}
        self.__eat_token(TokenType.ID)

        while self.current_token.type == TokenType.COMMA:
            self.__eat_token(TokenType.COMMA)
            if self.current_token.value in seen:
                self.error(ErrorCode.DUPLICATE_ID, self.current_token)
            seen.add(self.current_token.value)
            field_nodes.append(Ident(self.current_token, self.current_token.value))
            self.__eat_token(TokenType.ID)

        self.__eat_token(TokenType.COLON)
        type_node = self.type_spec()
        return [VariableDeclaration(field_node.value, type_node) for field_node in field_nodes]

    def index_type(self):
        pass

    def compound_statement(self) -> Compound:
        """compound_statement: BEGIN statement_list END"""
        token = self.current_token
        self.__eat_token(TokenType.BEGIN)
        nodes = self.statement_list()
        self.__eat_token(TokenType.END)

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return self.set_location(root, token)

    def statement_list(self) -> list[Statement]:
        """statement_list: statement
                            | statement SEMI statement_list"""
        node = self.statement()
        results = [node]

        while self.current_token.type == TokenType.SEMI:
            self.__eat_token(TokenType.SEMI)
            results.append(self.statement())

        if self.current_token.type == TokenType.ID:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)

        return results

    def statement(self) -> Statement:
        """statement : compound_statement
                        | assignment_statement
                        | input_statement
                        | output_statement
                        | if_statement
                        | while_statement
                        | repeat_until_statement
                        | for_statement
                        | proccall_statement
                        | empty"""
        if self.current_token.type == TokenType.BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == TokenType.INTEGER_CONST and self.__peek_next_token_type() == TokenType.COLON:
            node = self.label_statement()
        elif self.current_token.type == TokenType.GOTO:
            node = self.goto_statement()
        elif self.current_token.type == TokenType.INPUT:
            node = self.input_statement()
        elif self.current_token.type == TokenType.ID and self.__is_with_field(self.current_token):
            node = self.assignment_statement()
        elif self.current_token.type == TokenType.ID and self.__is_io(self.current_token):
            node = self.output_statement()
        elif self.current_token.type == TokenType.ID and self.__is_procedure(self.current_token):
            node = self.proccall_statement()
        elif self.current_token.type == TokenType.ID and self.__is_variable(
                self.current_token): #and self.__peek_next_token_type() == TokenType.ASSIGN:
            node = self.assignment_statement()
        elif self.current_token.type == TokenType.IF:
            node = self.if_statement()
        elif self.current_token.type == TokenType.CASE:
            node = self.case_statement()
        elif self.current_token.type == TokenType.WHILE:
            node = self.while_statement()
        elif self.current_token.type == TokenType.REPEAT:
            node = self.repeat_until_statement()
        elif self.current_token.type == TokenType.FOR:
            node = self.for_statement()
        elif self.current_token.type == TokenType.WITH:
            node = self.with_statement()
        else:
            node = self.empty()
        return node

    def label_statement(self) -> LabelStatement:
        token = self.current_token
        label = self.current_token.value
        self.__eat_token(TokenType.INTEGER_CONST)
        self.__eat_token(TokenType.COLON)
        statement = self.statement()
        return self.set_location(LabelStatement(label, statement), token)

    def goto_statement(self) -> GotoStatement:
        token = self.current_token
        self.__eat_token(TokenType.GOTO)
        label = self.current_token.value
        self.__eat_token(TokenType.INTEGER_CONST)
        return self.set_location(GotoStatement(label), token)

    def assignment_statement(self) -> Assign:
        """assignment_statement : variable ASSIGN expr"""
        lhs = self.variable()
        token = self.current_token
        self.__eat_token(TokenType.ASSIGN)
        rhs = self.expr()
        node = Assign(lhs, token, rhs)
        return self.set_location(node, lhs.token)

    def proccall_statement(self):
        """proccall_statement: ID IPAREN (expr (COMMA expr)*)? RPAREN"""
        token = self.current_token

        proc_name = token.value

        self.__eat_token(TokenType.ID)
        actual_params = []

        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)

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

        return self.set_location(node, token)

    def if_statement(self) -> IFStatement:
        """if_statement: IF expression THEN statement [ELSE statement]"""
        token = self.current_token
        self.__eat_token(TokenType.IF)
        expr = self.expr()
        self.__eat_token(TokenType.THEN)
        statement = self.statement()
        else_statement = None
        if self.current_token.type == TokenType.ELSE:
            self.__eat_token(TokenType.ELSE)
            else_statement = self.statement()
        return self.set_location(IFStatement(expr, statement, else_statement), token)

    def case_statement(self) -> CaseStatement:
        """case_statement: CASE expr OF case_branch* [ELSE statement] END"""
        token = self.current_token
        self.__eat_token(TokenType.CASE)
        expr = self.expr()
        self.__eat_token(TokenType.OF)

        branches = []
        else_statement = None
        while self.current_token.type not in [TokenType.ELSE, TokenType.END]:
            labels = [self.get_constant()]
            while self.current_token.type == TokenType.COMMA:
                self.__eat_token(TokenType.COMMA)
                labels.append(self.get_constant())

            self.__eat_token(TokenType.COLON)
            statement = self.statement()
            branches.append((labels, statement))

            if self.current_token.type == TokenType.SEMI:
                self.__eat_token(TokenType.SEMI)
            elif self.current_token.type not in [TokenType.ELSE, TokenType.END]:
                self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)

        if self.current_token.type == TokenType.ELSE:
            self.__eat_token(TokenType.ELSE)
            else_statement = self.statement()
            if self.current_token.type == TokenType.SEMI:
                self.__eat_token(TokenType.SEMI)

        self.__eat_token(TokenType.END)
        return self.set_location(CaseStatement(expr, branches, else_statement), token)

    def while_statement(self) -> WhileStatement:
        """while_statement: WHILE expression DO statement"""
        token = self.current_token
        self.__eat_token(TokenType.WHILE)
        expr = self.expr()
        self.__eat_token(TokenType.DO)
        statement = self.statement()
        return self.set_location(WhileStatement(expr, statement), token)

    def repeat_until_statement(self) -> RepeatUntilStatement:
        """repeat_until_statement: REPEAT statement_list UNTIL expr"""
        token = self.current_token
        self.__eat_token(TokenType.REPEAT)
        statements = []

        while self.current_token.type != TokenType.UNTIL:
            statements.append(self.statement())
            if self.current_token.type == TokenType.SEMI:
                self.__eat_token(TokenType.SEMI)
            elif self.current_token.type != TokenType.UNTIL:
                self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)

        self.__eat_token(TokenType.UNTIL)
        expr = self.expr()
        return self.set_location(RepeatUntilStatement(statements, expr), token)

    def for_statement(self) -> ForStatement:
        """for_statement : FOR ID ASSIGN expr [to|downto] expr do statement"""
        token = self.current_token
        self.__eat_token(TokenType.FOR)
        if self.current_token.type == TokenType.ID and self.__is_variable(self.current_token):
            id = self.variable()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
        self.__eat_token(TokenType.ASSIGN)
        expr1 = self.expr()
        if (self.current_token.type == TokenType.TO) or (self.current_token.type == TokenType.DOWNTO):
            dir = self.current_token
            self.__eat_token(self.current_token.type)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token)
        expr2 = self.expr()
        self.__eat_token(TokenType.DO)
        statement = self.statement()
        return self.set_location(ForStatement(id, expr1, dir, expr2, statement), token)

    def with_statement(self) -> WithStatement:
        """with_statement : WITH variable DO statement"""
        token = self.current_token
        self.__eat_token(TokenType.WITH)
        record = self.variable()
        self.__eat_token(TokenType.DO)
        self.with_records.append(record)
        statement = self.statement()
        self.with_records.pop()
        return self.set_location(WithStatement(record, statement), token)


    def output_statement(self) -> Output:
        """output_statement : WRITELN LPAREN output_field_list RPAREN"""
        token = self.current_token
        self.__eat_token(TokenType.ID)
        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)
            arguments = self.output_field_list()
            self.__eat_token(TokenType.RPAREN)
            return self.set_location(Output(token, arguments), token)
        return self.set_location(Output(token, None), token)

    def output_field_list(self):
        if self.current_token.type == TokenType.RPAREN:
            return []
        fields = [self.output_field()]
        while self.current_token.type == TokenType.COMMA:
            self.__eat_token(TokenType.COMMA)
            fields.append(self.output_field())
        return fields

    def output_field(self):
        value = self.expr()
        width = None
        precision = None
        if self.current_token.type == TokenType.COLON:
            self.__eat_token(TokenType.COLON)
            width = self.expr()
            if self.current_token.type == TokenType.COLON:
                self.__eat_token(TokenType.COLON)
                precision = self.expr()
        return OutputField(value, width, precision)

    def input_statement(self) -> Input:
        """input_statement : READLN [LPAREN exprList RPAREN]"""
        token = self.current_token
        self.__eat_token(TokenType.INPUT)
        arguments = []
        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)
            if self.current_token.type != TokenType.RPAREN:
                arguments = self.expr_list()
            self.__eat_token(TokenType.RPAREN)
        return self.set_location(Input(token, arguments), token)

    def variable(self) -> Ident:
        """variable: ID"""

        if self.__is_with_field(self.current_token):
            node = FieldVariable(self.with_records[-1], Ident(self.current_token, self.current_token.value))
            self.__eat_token(TokenType.ID)
        elif self.__is_array_varaible(self.current_token) and self.__peek_next_token_type() == TokenType.LEFT_BRACKET:
            array_identifier = Ident(self.current_token, self.current_token.value)
            self.__eat_token(TokenType.ID)
            self.__eat_token(TokenType.LEFT_BRACKET)
            index_expressions = [self.expr()]
            while self.current_token.type == TokenType.COMMA:
                self.__eat_token(TokenType.COMMA)
                index_expressions.append(self.expr())
            self.__eat_token(TokenType.RIGHT_BRACKET)
            node = IndexedVariable(array_identifier, index_expressions[0], index_expressions)
        else:
            node = Ident(self.current_token, self.current_token.value)
            self.__eat_token(TokenType.ID)

        while self.current_token.type in [TokenType.CARET, TokenType.DOT]:
            if self.current_token.type == TokenType.CARET:
                self.__eat_token(TokenType.CARET)
                node = DereferenceVariable(node)
            else:
                self.__eat_token(TokenType.DOT)
                field_name = Ident(self.current_token, self.current_token.value)
                self.__eat_token(TokenType.ID)
                node = FieldVariable(node, field_name)
        return node

    def __is_with_field(self, token: Token):
        if not self.with_records or token.type != TokenType.ID:
            return False
        record_type = self.__variable_type_node(self.with_records[-1])
        if not isinstance(record_type, RecordType):
            return False
        return any(field.name == token.value for field in record_type.fields)

    def __variable_type_node(self, node):
        if isinstance(node, Ident):
            symbol = self.current_scope.lookup(node.value, False)
            if symbol is None:
                self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.token)
            return symbol.type_node
        if isinstance(node, FieldVariable):
            record_type = self.__variable_type_node(node.record)
            if not isinstance(record_type, RecordType):
                self.error(ErrorCode.TYPE_ERROR, node.token)
            for field in record_type.fields:
                if field.name == node.field_name.value:
                    return field.type
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.field_name.token)
        if isinstance(node, DereferenceVariable):
            pointer_type = self.__variable_type_node(node.pointer)
            if not isinstance(pointer_type, PointerType):
                self.error(ErrorCode.TYPE_ERROR, node.token)
            return pointer_type.referenced_type
        if isinstance(node, IndexedVariable):
            symbol = self.current_scope.lookup(node.name.value, False)
            if symbol is None:
                self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.name.token)
            type_node = symbol.type_node
            if isinstance(type_node, ArrayType) and len(node.index_expressions) == len(type_node.indexTypes):
                return type_node.componentType
            if isinstance(type_node, ArrayType) and len(type_node.indexTypes) == 1:
                return type_node.componentType
            self.error(ErrorCode.TYPE_ERROR, node.token)
        return None

    def identifier(self):
        node = Ident(self.current_token, self.current_token.value)
        self.__eat_token(TokenType.ID)
        return node

    def resolve_constant(self) -> Ident:
        symbol = self.current_scope.lookup(self.current_token.value)
        # node = Ident(self.current_token, self.current_token.value)
        self.__eat_token(TokenType.ID)
        return symbol.value

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
        """term : factor ((MUL | INTEGER_DIV | MOD | FLOAT_DIV) factor)*"""
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
        actual_params = []

        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)

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
                    | BOOLEAN_CONST
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

        if token.type == TokenType.NOT:
            self.__eat_token(TokenType.NOT)
            return UnaryOp(token, self.factor())

        const = self.get_constant()
        if const is not None:
            return const

        if self.current_token.type == TokenType.LPAREN:
            self.__eat_token(TokenType.LPAREN)
            node = self.expr()
            self.__eat_token(TokenType.RPAREN)
            return node

        if self.current_token.type == TokenType.LEFT_BRACKET:
            return self.set_literal()

        if (
                self.current_token.type == TokenType.ID and
                self.__peek_next_token_type() == TokenType.LPAREN and
                self.__is_function(self.current_token)
        ):
            node = self.funccall_expression()
            return node

        if self.current_token.type == TokenType.ID and self.__is_with_field(self.current_token):
            node = self.variable()
            return node

        if self.current_token.type == TokenType.ID and self.__is_variable(self.current_token):
            node = self.variable()
            return node

        if self.current_token.type == TokenType.ID and self.__is_constant(self.current_token):
            node = self.resolve_constant()
            return node

    def set_literal(self):
        token = self.current_token
        self.__eat_token(TokenType.LEFT_BRACKET)
        elements = []
        if self.current_token.type != TokenType.RIGHT_BRACKET:
            elements.append(self.set_element())
            while self.current_token.type == TokenType.COMMA:
                self.__eat_token(TokenType.COMMA)
                elements.append(self.set_element())
        self.__eat_token(TokenType.RIGHT_BRACKET)
        return SetLiteral(token, elements)

    def set_element(self):
        lower = self.simple_expr()
        if self.current_token.type == TokenType.DOTDOT:
            self.__eat_token(TokenType.DOTDOT)
            return (lower, self.simple_expr())
        return lower

    def get_constant(self) -> Constant:
        token = self.current_token
        if token.type == TokenType.INTEGER_CONST:
            self.__eat_token(TokenType.INTEGER_CONST)
            return IntegerConstant(token)

        if token.type == TokenType.REAL_CONST:
            self.__eat_token(TokenType.REAL_CONST)
            return RealConstant(token)

        if token.type == TokenType.STRING_CONST:
            self.__eat_token(TokenType.STRING_CONST)
            return StringConstant(token)

        if token.type == TokenType.CHAR_CONST:
            self.__eat_token(TokenType.CHAR_CONST)
            return CharConstant(token)

        if token.type == TokenType.BOOLEAN_CONST:
            self.__eat_token(TokenType.BOOLEAN_CONST)
            return BooleanConstant(token)

        if token.type == TokenType.NIL:
            self.__eat_token(TokenType.NIL)
            return NilConstant(token)

        if token.type == TokenType.ID:
            symbol = self.current_scope.lookup(token.value, False) if self.current_scope is not None else None
            if isinstance(symbol, ConstSymbol):
                return self.resolve_constant()

        return None

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
        if self.current_scope is None:
            return True
        symbol = self.current_scope.lookup(token.value, False)
        if symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=token)
        return isinstance(symbol, VarSymbol)

    def __is_array_varaible(self, token: Token):
        if not token.type == TokenType.ID:
            self.error(error_code=ErrorCode.EXPECTED_IDENTIFIER, token=token)
        if self.current_scope is None:
            return False
        symbol = self.current_scope.lookup(token.value, False)
        if symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=token)
        return isinstance(symbol, VarSymbol) and symbol.type == DataType.ARRAY


    def __is_constant(self, token: Token) -> bool:
        if not token.type == TokenType.ID:
            self.error(error_code=ErrorCode.EXPECTED_IDENTIFIER, token=token)
        if self.current_scope is None:
            return False
        symbol = self.current_scope.lookup(token.value, False)
        if symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=token)
        return isinstance(symbol, ConstSymbol)

    def __is_procedure(self, token: Token) -> bool:
        if not token.type == TokenType.ID:
            self.error(error_code=ErrorCode.EXPECTED_IDENTIFIER, token=token)
        if self.current_scope is None:
            return False
        symbol = self.current_scope.lookup(token.value, False)
        if symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=token)
        return isinstance(symbol, ProcedureSymbol)

    def __is_function(self, token: Token) -> bool:
        if not token.type == TokenType.ID:
            self.error(error_code=ErrorCode.EXPECTED_IDENTIFIER, token=token)
        if self.current_scope is None:
            return False
        symbol = self.__lookup_function(token.value)
        if symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=token)
        return isinstance(symbol, FunctionSymbol)

    def __lookup_function(self, name: str):
        scope = self.current_scope
        while scope is not None:
            symbol = scope._symbols.get(name)
            if isinstance(symbol, FunctionSymbol):
                return symbol
            scope = scope.enclosing_scope
        return None

    def __is_io(self, token: Token) -> bool:
        if not token.type == TokenType.ID:
            self.error(error_code=ErrorCode.EXPECTED_IDENTIFIER, token=token)
        if self.current_scope is None:
            return False
        symbol = self.current_scope.lookup(token.value, False)
        if symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=token)
        return isinstance(symbol, BuiltinIOSymbol)
