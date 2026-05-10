from .error_code import SemanticError, ErrorCode
from .data_type import DataType
from .token_type import TokenType
from .symbol import ScopedSymbolTable, VarSymbol, ProcedureSymbol, FunctionSymbol, BuiltinFunctionSymbol
from .pascal_ast import NodeVisitor, AST, LabelStatement, GotoStatement, IFStatement, CaseStatement, WhileStatement, BinaryOp, Assign, Ident, \
    VariableDeclaration, \
    ProcedureDeclaration, ProcedureCall, FunctionDeclaration, FunctionCall, Type, Output, Input, \
    UnaryOp, ForStatement, RepeatUntilStatement, IndexedVariable, FieldVariable, ArrayType, RecordType, WithStatement


class SemanticAnalyzer(NodeVisitor):
    def __init__(self, tree: AST):
        self.tree = tree
        self.current_scope: ScopedSymbolTable = None
        self.integer_ops = [TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.MOD, TokenType.INTEGER_DIV,
                            TokenType.REAL_DIV,
                            TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.EQUAL, TokenType.NOT_EQUAL,
                            TokenType.GREATER_EQUAL, TokenType.GREATER, TokenType.LESS, TokenType.LESS_EQUAL]
        self.real_ops = [TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.REAL_DIV, TokenType.EQUAL,
                         TokenType.NOT_EQUAL, TokenType.GREATER_EQUAL, TokenType.GREATER, TokenType.LESS, TokenType.LESS_EQUAL]
        self.boolean_ops = [TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.GREATER_EQUAL, TokenType.GREATER,
            TokenType.LESS, TokenType.LESS_EQUAL, TokenType.AND, TokenType.OR]

    def analyze(self):
        tree = self.tree
        if tree is None:
            return ''
        return self.visit(self.tree)

    def error(self, error_code, token):
        raise SemanticError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}'
        )

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_Program(self, node):
        #print('ENTER scope: global')
        global_scope = ScopedSymbolTable(
            scope_name = 'global',
            scope_level = 1,
            enclosing_scope=self.current_scope
        )
        global_scope.init_builtins()
        self.current_scope = global_scope

        self.visit(node.block)
        #print(global_scope)

        self.current_scope = self.current_scope.enclosing_scope
        #print('LEAVE scope: global')


    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_Output(self, node: Output):
        if node.arguments is not None:
            for argument in node.arguments:
                self.visit(argument)

    def visit_Input(self, node: Input):
        if node.arguments is not None:
            for argument in node.arguments:
                self.visit(argument)

    def visit_ProcedureDeclaration(self, node: ProcedureDeclaration):
        proc_name = node.proc_name
        proc_symbol = ProcedureSymbol(proc_name)
        self.current_scope.insert(proc_symbol)

        #print('ENTER scope: %s' % proc_name)
        procedure_scope = ScopedSymbolTable(
            scope_name=proc_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = procedure_scope

        for param in node.params or []:
            param_name = param.name
         #   param_type = self.current_scope.lookup(param_name)
            param_type = param.type
            var_symbol = VarSymbol(param_name, param_type.data_type, param.by_reference, param_type)
            self.current_scope.insert(var_symbol)
            proc_symbol.formal_params.append(var_symbol)

        proc_symbol.block_ast = node.block_node
        self.visit(node.block_node)

        #print(procedure_scope)

        self.current_scope = self.current_scope.enclosing_scope
        #print('LEAVE scope: %s' % proc_name)

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        func_name = node.func_name
        func_symbol = FunctionSymbol(func_name, node.return_type.data_type)
        self.current_scope.insert(func_symbol)

        #print('ENTER scope: %s' % func_name)
        function_scope = ScopedSymbolTable(
            scope_name=func_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = function_scope

        for param in node.params or []:
            param_type = param.type.data_type
            param_name = param.name
            var_symbol = VarSymbol(param_name, param_type, param.by_reference, param.type)
            self.current_scope.insert(var_symbol)
            func_symbol.formal_params.append(var_symbol)

        func_symbol.return_type = node.return_type.data_type
        func_symbol.block_ast = node.block_node
        self.visit(node.block_node)

        #print(function_scope)

        self.current_scope = self.current_scope.enclosing_scope
        #print('LEAVE scope: %s' % func_name)


    def visit_VariableDeclaration(self, node: VariableDeclaration):
        if isinstance(node.type, ArrayType):
            var_type = DataType.ARRAY
        elif isinstance(node.type, RecordType):
            var_type = DataType.RECORD
        else:
            type_name = node.type.data_type.name
            type_symbol = self.current_scope.lookup(type_name)
            var_type = type_symbol.type

        var_name = node.name
        var_symbol = VarSymbol(var_name, var_type, type_node=node.type)

        if self.current_scope.lookup(var_name, current_scope_only=True):
            self.error(
                error_code=ErrorCode.DUPLICATE_ID,
                token=node.type.token,
            )
        self.current_scope.insert(var_symbol)

    def visit_ProcedureCall(self, node: ProcedureCall):
        proc_symbol = self.current_scope.lookup(node.proc_name)
        if len(proc_symbol.formal_params) != len(node.actual_params):
            self.error(
                error_code=ErrorCode.INCORRECT_NUM_OF_ARGS,
                token=node.token
            )

        for param_symbol, param_node in zip(proc_symbol.formal_params, node.actual_params):
            param_type = self.visit(param_node)
            if param_type != param_symbol.type:
                self.error(ErrorCode.TYPE_ERROR, node.token)
            if param_symbol.by_reference and not isinstance(param_node, Ident):
                self.error(ErrorCode.TYPE_ERROR, node.token)

        proc_symbol = self.current_scope.lookup(node.proc_name)
        # accessed by the interpreter when executing procedure call
        node.proc_symbol = proc_symbol

    def visit_FunctionCall(self, node: FunctionCall):
        func_symbol = self.lookup_function(node.func_name)
        if isinstance(func_symbol, BuiltinFunctionSymbol):
            if func_symbol.arity != len(node.actual_params):
                self.error(
                    error_code=ErrorCode.INCORRECT_NUM_OF_ARGS,
                    token=node.token
                )
            arg_types = [self.visit(param_node) for param_node in node.actual_params]
            node.func_symbol = func_symbol
            if node.func_name in ["ABS", "SQR"]:
                if arg_types[0] not in [DataType.INTEGER, DataType.REAL]:
                    self.error(ErrorCode.TYPE_ERROR, node.token)
                return arg_types[0]
            if node.func_name == "ODD" and arg_types[0] != DataType.INTEGER:
                self.error(ErrorCode.TYPE_ERROR, node.token)
            if node.func_name == "ORD" and arg_types[0] not in [DataType.INTEGER, DataType.CHAR, DataType.BOOLEAN]:
                self.error(ErrorCode.TYPE_ERROR, node.token)
            if node.func_name == "CHR" and arg_types[0] != DataType.INTEGER:
                self.error(ErrorCode.TYPE_ERROR, node.token)
            if node.func_name in ["PRED", "SUCC"]:
                if arg_types[0] not in [DataType.INTEGER, DataType.CHAR]:
                    self.error(ErrorCode.TYPE_ERROR, node.token)
                return arg_types[0]
            if node.func_name in ["TRUNC", "ROUND"] and arg_types[0] not in [DataType.INTEGER, DataType.REAL]:
                self.error(ErrorCode.TYPE_ERROR, node.token)
            if node.func_name in ["SQRT", "EXP", "LN", "SIN", "COS", "ARCTAN"] and arg_types[0] not in [DataType.INTEGER, DataType.REAL]:
                self.error(ErrorCode.TYPE_ERROR, node.token)
            return func_symbol.return_type

        if len(func_symbol.formal_params) != len(node.actual_params):
            self.error(
                error_code=ErrorCode.INCORRECT_NUM_OF_ARGS,
                token=node.token
            )

        for param_symbol, param_node in zip(func_symbol.formal_params, node.actual_params):
            param_type = self.visit(param_node)
            if param_type != param_symbol.type:
                self.error(ErrorCode.TYPE_ERROR, node.token)
            if param_symbol.by_reference and not isinstance(param_node, Ident):
                self.error(ErrorCode.TYPE_ERROR, node.token)

        # accessed by the interpreter when executing function call
        node.func_symbol = func_symbol
        return func_symbol.return_type

    def lookup_function(self, name):
        scope = self.current_scope
        while scope is not None:
            symbol = scope._symbols.get(name)
            if isinstance(symbol, FunctionSymbol):
                return symbol
            scope = scope.enclosing_scope
        return None


    def visit_Ident(self, node: Ident):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.token)
        return var_symbol.type

    def visit_IntegerConstant(self, node):
        return node.type.data_type

    def visit_RealConstant(self, node):
        return node.type.data_type

    def visit_StringConstant(self, node):
        return node.type.data_type

    def visit_CharConstant(self, node):
        return node.type.data_type

    def visit_BooleanConstant(self, node):
        return node.type.data_type

    def visit_Assign(self, node: Assign):
        lhstype: DataType = self.visit(node.lhs)
        rhstype: DataType = self.visit(node.rhs)
        if lhstype != rhstype:
            self.error(ErrorCode.TYPE_ERROR, node.token)

    def visit_LabelStatement(self, node: LabelStatement):
        self.visit(node.statement)

    def visit_GotoStatement(self, node: GotoStatement):
        pass

    def visit_IndexedVariable(self, node: IndexedVariable):
        array_symbol = self.current_scope.lookup(node.name.value)
        if array_symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.name.token)
        self.visit(node.index_expression)
        if isinstance(array_symbol.type_node, ArrayType):
            return array_symbol.type_node.componentType.data_type
        return DataType.INTEGER

    def visit_FieldVariable(self, node: FieldVariable):
        field = self.record_field(node)
        node.field_declaration = field
        return field.type.data_type

    def variable_type_node(self, node):
        if isinstance(node, Ident):
            symbol = self.current_scope.lookup(node.value)
            if symbol is None:
                self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.token)
            return symbol.type_node
        if isinstance(node, IndexedVariable):
            symbol = self.current_scope.lookup(node.name.value)
            if symbol is None:
                self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.name.token)
            if isinstance(symbol.type_node, ArrayType):
                return symbol.type_node.componentType
        if isinstance(node, FieldVariable):
            return self.record_field(node).type
        return None

    def record_field(self, node: FieldVariable):
        record_type = self.variable_type_node(node.record)
        if not isinstance(record_type, RecordType):
            self.error(ErrorCode.TYPE_ERROR, node.token)
        for field in record_type.fields:
            if field.name == node.field_name.value:
                return field
        self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.field_name.token)

    def visit_UnaryOp(self, node: UnaryOp):
        operand_type = self.visit(node.operand)
        if node.op.type == TokenType.NOT and operand_type != DataType.BOOLEAN:
            self.error(ErrorCode.TYPE_ERROR, node.op)
        return operand_type

    def is_valid_bin_op(self, data_type, op):
        if data_type == DataType.INTEGER:
            return op.type in self.integer_ops
        if data_type == DataType.REAL:
            return op.type in self.real_ops
        if data_type == DataType.STRING:
            return False
        if data_type == DataType.BOOLEAN:
            return op.type in self.boolean_ops
        return False

    def visit_BinaryOp(self, node: BinaryOp):
        lhstype: DataType = self.visit(node.lhs)
        rhstype: DataType = self.visit(node.rhs)
        if lhstype != rhstype:
            self.error(ErrorCode.TYPE_ERROR, node.token)
        if not self.is_valid_bin_op(lhstype, node.op):
            self.error(ErrorCode.INVALID_OPERATION, node.token)
        if node.op.type == TokenType.REAL_DIV:
            return DataType.REAL
        if node.op.type in self.boolean_ops:
            return DataType.BOOLEAN
        return lhstype

    def visit_IFStatement(self, node: IFStatement):
        self.visit(node.expr)
        self.visit(node.statement)
        self.visit(node.else_statement)

    def visit_CaseStatement(self, node: CaseStatement):
        self.visit(node.expr)
        for labels, statement in node.branches:
            for label in labels:
                self.visit(label)
            self.visit(statement)
        self.visit(node.else_statement)

    def visit_WhileStatement(self, node: WhileStatement):
        self.visit(node.expr)
        self.visit(node.statement)

    def visit_RepeatUntilStatement(self, node: RepeatUntilStatement):
        for statement in node.statements:
            self.visit(statement)
        self.visit(node.expr)

    def visit_ForStatement(self, node: ForStatement):
        self.visit(node.id)
        self.visit(node.expr1)
        self.visit(node.expr2)
        self.visit(node.statement)

    def visit_WithStatement(self, node: WithStatement):
        record_type = self.variable_type_node(node.record)
        if not isinstance(record_type, RecordType):
            self.error(ErrorCode.TYPE_ERROR, node.token)
        self.visit(node.statement)
