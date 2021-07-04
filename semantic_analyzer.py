from symbol import ScopedSymbolTable, BuiltinTypeSymbol, VarSymbol, ProcedureSymbol
from ast import NodeVisitor, AST, IFStatement, WhileStatement, BinaryOp, Assign, Var, VariableDeclaration, \
    ProcedureDeclaration


class SemanticAnalyzer(NodeVisitor):
    def __init__(self, tree: AST):
        self.tree = tree
        self.results = {}
        self.current_scope: ScopedSymbolTable = None

    def analyze(self):
        tree = self.tree
        if tree is None:
            return ''
        tree.accept(self)
        return self.results.get(self.tree)

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
        global_scope._init_builtins()
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
            proc_symbol.params.append(var_symbol)

        # self.visit(node.block_node)
        node.block_node.accept(self)

        print(procedure_scope)

        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: %s' % proc_name)

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name)

        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)

        if self.current_scope.lookup(var_name, current_scope_only=True):
            raise Exception(
                "Error: Duplicate identifier '%s' found" % var_name
            )
        self.current_scope.insert(var_symbol)

    def visit_Var(self, node: Var):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise Exception(
                "Error: Symbol(identifier) not found '%s'" % var_name
            )

    def visit_Assign(self, node: Assign):
#        self.visit(node.lhs)
#        self.visit(node.rhs)
        node.lhs.accept(self)
        node.rhs.accept(self)

    def visit_BinaryOp(self, node: BinaryOp):
        # self.visit(node.lhs)
        # self.visit(node.rhs)
        node.lhs.accept(self)
        node.rhs.accept(self)

    def visit_IFStatement(self, node: IFStatement):
        node.expr.accept(self)
        node.statement.accept(self)
        node.eode.else_statement.accept(node)
        # if (self.visit(node.expr)):
        #     self.visit(node.statement)
        # else:
        #     self.visit(node.else_statement)

    def visit_WhileStatement(self, node: WhileStatement):
        node.expr.accept(self)
        node.statement.accept(self)
        # while(self.visit(node.expr)):
        #     self.visit(node.statement)