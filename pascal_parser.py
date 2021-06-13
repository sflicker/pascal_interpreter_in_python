
from pascal_tokenizer import TokenType

class AST(object):
    def __init__(self):
        pass

class Program(AST):
    def __init__(self, name, block):
        self.name = name
        self.block = block

class ProcedureDecl(AST):
    def __init__(self, proc_name, block_node):
        self.proc_name = proc_name
        self.block_node = block_node

class Block(AST):
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement

class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node

class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.number = token.value

class String(AST):
    def __init__(self, value):
        self.value = value

class BinaryOp(AST):
    def __init__(self, lhs, op, rhs):
        self.op = op
        self.token = op
        self.lhs = lhs
        self.rhs = rhs

class UnaryOp(AST):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class Compound(AST):
    """Represents a 'BEGIN ... END' block"""
    def __init__(self):
        self.children = []

class Writeln(AST):
    def __init__(self, arguments):
        self.arguments = arguments

class Assign(AST):
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = self.token = op
        self.rhs = rhs

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class NoOp(AST):
    def __init(self):
        pass

class Parser(object):
    """Parser accepts a list of tokens and returns an abstract syntax tree"""

    def __init__(self, tokens):
        self.tokens = tokens
        self.token_pos = 0
        self.current_token = self.tokens[self.token_pos]

    def get_parsed_tree(self):
        """
            expr -> term ((PLUS|MINUS) term)*
            term -> factor ((MUL|DIV) factor)*
            factor -> NUMBER|-factor|LPAREN expr RPAREN
        """

        root = self.program()
        if self.current_token.type != TokenType.EOF:
            raise Exception("Parse Exception")
        return root

    def program(self):
        """program : PROGRAM variable SEMI block DOT"""
        self.__eat_token(TokenType.PROGRAM)
        var_node = self.variable()
        prog_name = var_node.value
        self.__eat_token(TokenType.SEMI)
        block_node = self.block()
        program_node = Program(prog_name, block_node)
        self.__eat_token(TokenType.DOT)
        return program_node

    def block(self):
        """block : declarations compound_statement"""
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes, compound_statement_node)
        return node

    def declarations(self):
        """declarations : VAR (variable_declaration SEMI)+
                        | (PROCEDURE ID SEMI block SEMI)*
                        | empty
        """
        declarations = []
        if self.current_token.type == TokenType.VAR:
            self.__eat_token(TokenType.VAR)
            while self.current_token.type == TokenType.ID:
                var_decl = self.variable_declaration()
                declarations.extend(var_decl)
                self.__eat_token(TokenType.SEMI)

        while self.current_token.type == TokenType.PROCEDURE:
            self.__eat_token(TokenType.PROCEDURE)
            proc_name = self.current_token.value
            self.__eat_token(TokenType.ID)
            self.__eat_token(TokenType.SEMI)
            block_node = self.block()
            proc_decl = ProcedureDecl(proc_name, block_node)
            declarations.append(proc_decl)
            self.__eat_token(TokenType.SEMI)

        return declarations

    def variable_declaration(self):
        """variable_declaration : ID (COMMA ID)* COLON type_spec"""
        var_nodes = [Var(self.current_token)] # first ID
        self.__eat_token(TokenType.ID)

        while self.current_token.type == TokenType.COMMA:
            self.__eat_token(TokenType.COMMA)
            var_nodes.append(Var(self.current_token))
            self.__eat_token(TokenType.ID)

        self.__eat_token(TokenType.COLON)

        type_node = self.type_spec()
        var_declarations = [VarDecl(var_node, type_node) for var_node in var_nodes]
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

    def compound_statement(self):
        """compound_statement: BEGIN statement_list END"""
        self.__eat_token(TokenType.BEGIN)
        nodes = self.statement_list()
        self.__eat_token(TokenType.END)

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self):
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

    def statement(self):
        """statement : compound_statement
                        | assignment_statement
                        | iostatement
                        | empty"""
        if self.current_token.type == TokenType.BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == TokenType.ID:
            node = self.assignment_statement()
        elif self.current_token.type == TokenType.WRITELN:
            node = self.iostatement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        """assignment_statement : variable ASSIGN expr"""
        lhs = self.variable()
        token = self.current_token
        self.__eat_token(TokenType.ASSIGN)
        rhs = self.expr()
        node = Assign(lhs, token, rhs)
        return node

    def iostatement(self):
        """iostatement : WRITELN LPAREN exprList RPAREN"""
        token = self.current_token
        self.__eat_token(TokenType.WRITELN)
        self.__eat_token(TokenType.LPAREN)
        arguments = self.expr_list()
        self.__eat_token(TokenType.RPAREN)
        return Writeln(arguments)

    def variable(self):
        """variable: ID"""
        node = Var(self.current_token)
        self.__eat_token(TokenType.ID)
        return node

    def empty(self):
        """an empty production"""
        return NoOp()

    def expr_list(self):
        """exprList: expr (, expr)*"""
        root_expr = self.expr()
        curr_expr = root_expr
        while self.current_token.type == TokenType.COMMA:
            self.__eat_token(TokenType.COMMA)
            next_expr = self.expr()
            curr_expr.next = next_expr
            curr_expr = next_expr
            curr_expr.next = None

        return root_expr

    def expr(self):
        """expr : term ((PLUS | MINUS) term)*"""
        root = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            lhs = root
            op = self.current_token

            if op.type == TokenType.PLUS:
                self.__eat_token(TokenType.PLUS)
            elif op.type == TokenType.MINUS:
                self.__eat_token(TokenType.MINUS)

            rhs = self.term()

            root = BinaryOp(lhs, op, rhs)
        return root

    def term(self):
        """term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)*"""
        root = self.factor()

        while self.current_token.type in (TokenType.MUL, TokenType.REAL_DIV, TokenType.INTEGER_DIV):
            lhs = root
            op = self.current_token

            if op.type == TokenType.MUL:
                self.__eat_token(TokenType.MUL)
            elif op.type == TokenType.INTEGER_DIV:
                self.__eat_token(TokenType.INTEGER_DIV)
            elif op.type == TokenType.REAL_DIV:
                self.__eat_token(TokenType.REAL_DIV)

            rhs = self.factor()
            root = BinaryOp(lhs, op, rhs)

        return root

    def factor(self):
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

    def __advance_token(self):
        if self.current_token.type != TokenType.EOF:
            self.token_pos = self.token_pos + 1
            self.current_token = self.tokens[self.token_pos]

    def __eat_token(self, token_type):
        if self.current_token.type == token_type:
            self.__advance_token()
        else:
            raise Exception("Parse Exception - Expected Type", token_type, ", Found", self.current_token.type)
