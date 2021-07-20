import ast
import enum

from ast import NodeVisitor


###########################
## Symbols and Symbol Table
###########################
from token_type import TokenType


class SymbolKind(enum.Enum):
    VAR = "Variable"
    PROC = "Procedure"
    FUNC = "Function"
    TYPE = "Type"

class Symbol(object):
    def __init__(self, name: str, a_type=None, kind=None):
        self.name: str = name
        self.type = a_type
        self.kind = kind
        self.scope_level = 0

class VarSymbol(Symbol):
    def __init__(self, name: str, type: ast.Type):
        super().__init__(name, type)

    def __str__(self):
        return "<{class_name}(name='{name}, type='{type}', kind='{kind}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
            kind=self.kind
        )

    __repr__ = __str__

class TypeSymbol(Symbol):
    def __init__(self, name: str):
        super().__init__(name)

    def __repr__(self):
        return "<{class_name}(name='{name}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
        )

class BuiltinTypeSymbol(TypeSymbol):
    def __init__(self, name: str):
        super().__init__(name)

    def __str__(self):
        return self.name


class ProcedureSymbol(Symbol):
    def __init__(self, name, params=None):
        super().__init__(name, None, SymbolKind.PROC)
        #a list of formal parameters
        self.formal_params = params if params is not None else []
        # a reference to procedure's body
        self.block_ast = None

    def __str__(self):
        return '<{class_name}(name={name}, parameters={params})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            params=self.formal_params,
        )

    __repr__ = __str__

class FunctionSymbol(Symbol):
    def __init__(self, name, return_type, params=None):
        super().__init__(name, return_type, SymbolKind.FUNC)
        self.return_type = return_type
        self.formal_params = params if params is not None else []
        self.block_ast = None

    def __str__(self):
        return '<{class_name}(name={name}, parameters={params}, type={type})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            params=self.formal_params,
            type=self.type,
        )

    __repr__ = __str__


class ScopedSymbolTable(object):
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbols = {}
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def init_builtins(self):
        self.insert(BuiltinTypeSymbol('INTEGER'))
        self.insert(BuiltinTypeSymbol('REAL'))
        self.insert(BuiltinTypeSymbol('STRING'))

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope',
             self.enclosing_scope.scope_name if self.enclosing_scope else None
            )
        ):
            lines.append('%-15s: %s' % (header_name, header_value))
        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s


    __repr__ = __str__

    def insert(self, symbol):
        print('Insert: %s' % symbol.name)
        symbol.scope_level = self.scope_level
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str, current_scope_only=False) -> Symbol:
        print('Lookup: %s, (Scope name: %s)' % (name, self.scope_name))
        symbol = self._symbols.get(name)

        if symbol is not None:
            return symbol

        if current_scope_only:
            return None

        #recursively go up the chain
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)
