from error_code import SemanticError, ErrorCode
from symbol import ScopedSymbolTable, VarSymbol, ProcedureSymbol, FunctionSymbol
from ast import NodeVisitor, AST, IFStatement, WhileStatement, BinaryOp, Assign, Ident, VariableDeclaration, \
    ProcedureDeclaration, ProcedureCall, FunctionDeclaration, FunctionCall


class SemanticAnalyzer(NodeVisitor):
    def __init__(self, tree: AST):
        self.tree = tree
        self.current_scope: ScopedSymbolTable = None

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
        print('ENTER scope: global')
        global_scope = ScopedSymbolTable(
            scope_name = 'global',
            scope_level = 1,
            enclosing_scope=self.current_scope
        )
        global_scope.init_builtins()
        self.current_scope = global_scope

        self.visit(node.block)
        print(global_scope)

        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: global')


    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_ProcedureDeclaration(self, node: ProcedureDeclaration):
        proc_name = node.proc_name
        proc_symbol = ProcedureSymbol(proc_name)
        self.current_scope.insert(proc_symbol)

        print('ENTER scope: %s' % proc_name)
        procedure_scope = ScopedSymbolTable(
            scope_name=proc_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = procedure_scope

        for param in node.params:
            param_type = self.current_scope.lookup(param.type_node.value)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.insert(var_symbol)
            proc_symbol.formal_params.append(var_symbol)

        proc_symbol.block_ast = node.block_node
        self.visit(node.block_node)

        print(procedure_scope)

        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: %s' % proc_name)

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        func_name = node.func_name
        func_symbol = FunctionSymbol(func_name, node.return_type)
        self.current_scope.insert(func_symbol)

        print('ENTER scope: %s' % func_name)
        function_scope = ScopedSymbolTable(
            scope_name=func_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = function_scope

        for param in node.params:
            param_type = self.current_scope.lookup(param.type.value)
            param_name = param.name
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.insert(var_symbol)
            func_symbol.formal_params.append(var_symbol)

        func_symbol.return_type = node.return_type
        func_symbol.block_ast = node.block_node
        self.visit(node.block_node)

        print(function_scope)

        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: %s' % func_name)


    def visit_VariableDeclaration(self, node: VariableDeclaration):
        type_name = node.type.value
        type_symbol = self.current_scope.lookup(type_name)

        var_name = node.name
        var_symbol = VarSymbol(var_name, type_symbol)

        if self.current_scope.lookup(var_name, current_scope_only=True):
            self.error(
                error_code=ErrorCode.DUPLICATE_ID,
                token=node.var_node.token,
            )
        self.current_scope.insert(var_symbol)

    def visit_ProcedureCall(self, node: ProcedureCall):
        proc_symbol = self.current_scope.lookup(node.proc_name)
        if len(proc_symbol.formal_params) != len(node.actual_params):
            self.error(
                error_code=ErrorCode.INCORRECT_NUM_OF_ARGS,
                token=node.token
            )

        for param_node in node.actual_params:
            self.visit(param_node)

        proc_symbol = self.current_scope.lookup(node.proc_name)
        # accessed by the interpreter when executing procedure call
        node.proc_symbol = proc_symbol

    def visit_FunctionCall(self, node: FunctionCall):
        func_symbol = self.current_scope.lookup(node.func_name)
        if len(func_symbol.formal_params) != len(node.actual_params):
            self.error(
                error_code=ErrorCode.INCORRECT_NUM_OF_ARGS,
                token=node.token
            )

        for param_node in node.actual_params:
            self.visit(param_node)

        func_symbol = self.current_scope.lookup(node.func_name)
        # accessed by the interpreter when executing function call
        node.func_symbol = func_symbol


    def visit_Ident(self, node: Ident):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.token)

    def visit_Assign(self, node: Assign):
        self.visit(node.lhs)
        self.visit(node.rhs)

    def visit_BinaryOp(self, node: BinaryOp):
        self.visit(node.lhs)
        self.visit(node.rhs)

    def visit_IFStatement(self, node: IFStatement):
        self.visit(node.expr)
        self.visit(node.statement)
        self.visit(node.else_statement)

    def visit_WhileStatement(self, node: WhileStatement):
        self.visit(node.expr)
        self.visit(node.statement)
