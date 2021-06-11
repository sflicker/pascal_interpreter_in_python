# Instructions
# Given a mathematical expression as a string you must return the result as a number.
#
# Numbers
# Number may be both whole numbers and/or decimal numbers. The same goes for the returned result.
#
# Operators
# You need to support the following mathematical operators:
#
# Multiplication *
# Division / (as floating point division)
# Addition +
# Subtraction -
# Operators are always evaluated from left-to-right, and * and / must be evaluated before + and -.
#
# Parentheses
# You need to support multiple levels of nested parentheses, ex. (2 / (2 + 3.33) * 4) - -6
#
# Whitespace
# There may or may not be whitespace between numbers and operators.
#
# An addition to this rule is that the minus sign (-) used for negating numbers and parentheses will never be separated by whitespace. I.e all of the following are valid expressions.
#
# 1-1    // 0
# 1 -1   // 0
# 1- 1   // 0
# 1 - 1  // 0
# 1- -1  // 2
# 1 - -1 // 2
#
# 6 + -(4)   // 2
# 6 + -( -4) // 10
# And the following are invalid expressions
#
# 1 - - 1    // Invalid
# 1- - 1     // Invalid
# 6 + - (4)  // Invalid
# 6 + -(- 4) // Invalid
# Validation
# You do not need to worry about validation - you will only receive valid mathematical expressions following the above rules.
#
# Restricted APIs
# NOTE: eval and exec are disallowed in your solution.

import codewars_test as Test

import enum


class TokenType(enum.Enum):
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    NUMBER = "number"
    LPAREN = "{"
    RPAREN = "}"
    DOT = "."
    SEMI = ";"
    ASSIGN = ":="
    BEGIN = "begin"
    END = "end"
    IDIV = "div"
    ID = "identifier"
    EOF = "eof"


class Token(object):
    def __init__(self, type: TokenType, value: str):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token({type}, {value})".format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


RESERVED_KEYWORDS = {
    'BEGIN': Token(TokenType.BEGIN, 'BEGIN'),
    'END': Token(TokenType.END, 'END'),
    'DIV': Token(TokenType.IDIV, 'DIV')
}

class AST(object):
    def __init__(self):
        self.type = None


class Num(AST):
    def __init__(self, token):
        self.type = "Number"
        self.token = token
        self.number = token.value

class BinaryOp(AST):
    def __init__(self, lhs, op, rhs):
        self.type = "Op"
        self.op = op
        self.token = op
        self.lhs = lhs
        self.rhs = rhs

class UnaryOp(AST):
    def __init__(self, op, operand):
        self.type = "Negation"
        self.of = op
        self.operand = operand

class Compound(AST):
    """Represents a 'BEGIN ... END' block"""
    def __init__(self):
        self.type = "Compound"
        self.children = []

class Assign(AST):
    def __init__(self, left, op, right):
        self.type = "Assign"
        self.left = left
        self.op = self.token = op
        self.right = right

class Var(AST):
    def __init__(self, token):
        self.type = "Variable"
        self.token = token
        self.value = token.value

class NoOp(AST):
    def __init(self):
        self.type = "NoOp"




class Solver(object):
    def __init__(self):
        self.SYMBOL_TABLE = {}
        pass

    def solve(self, ast):
        if ast.type == "Compound":
            for child in ast.children:
                self.solve(child)
            return self.SYMBOL_TABLE
        if ast.type == "Assign":
            var_name = ast.left.value
            self.SYMBOL_TABLE[var_name] = self.solve(ast.right)
            return
        if ast.type == "Variable":
            var_name = ast.value
            val = self.SYMBOL_TABLE.get(var_name)
            if val is None:
                raise Exception("Unknown Symbol " + var_name)
            else:
                return val
        if ast.type == "Number":
            return float(ast.token.value)
        if ast.type == "Negation":
            operand = self.solve(ast.operand)
            return -operand
        if ast.type == "Op":
            lhs = self.solve(ast.lhs)
            rhs = self.solve(ast.rhs)
            if ast.token.type == TokenType.PLUS:
                return lhs + rhs
            if ast.token.type == TokenType.MINUS:
                return lhs - rhs
            if ast.token.type == TokenType.MUL:
                return lhs * rhs
            if ast.token.type == TokenType.DIV:
                return lhs / rhs
            if ast.token.type == TokenType.IDIV:
                return (int)(lhs/rhs)


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
        """program : compound_statement DOT"""
        node = self.compound_statement()
        self.__eat_token(TokenType.DOT)
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
                        | empty"""
        if self.current_token.type == TokenType.BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == TokenType.ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        """assignment_statement : variable ASSIGN expr"""
        left = self.variable()
        token = self.current_token
        self.__eat_token(TokenType.ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def variable(self):
        """variable: ID"""
        node = Var(self.current_token)
        self.__eat_token(TokenType.ID)
        return node

    def empty(self):
        """an empty production"""
        return NoOp()

    def expr(self):
        root = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            lhs = root
            op = self.current_token

            self.__advance_token()

            rhs = self.term()

            root = BinaryOp(lhs, op, rhs)
        return root

    def term(self):
        root = self.factor()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV, TokenType.IDIV):
            lhs = root
            op = self.current_token
            self.__advance_token()
            rhs = self.factor()
            root = BinaryOp(lhs, op, rhs)

        return root

    def factor(self):

        token = self.current_token

        if token.type == TokenType.NUMBER:
            self.__eat_token(TokenType.NUMBER)
            return Num(token)

        if token.type == TokenType.PLUS:
            self.__eat_token(TokenType.PLUS)
            return UnaryOp(token, self.factor())

        if token.type == TokenType.MINUS:
            self.__eat_token(TokenType.MINUS)
            return UnaryOp(token, self.factor())

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
            raise Exception("Parse Exception")


class Tokenizer(object):
    """Tokenizer accepts a text expression and returns a list of tokens"""

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    """Return a list of tokens"""

    def get_tokens(self):
        tokens = []
        while self.current_char is not None:
            token = self.__get_next_token()
            tokens.append(token)

        tokens.append(Token(TokenType.EOF, ""))
        return tokens

    def __get_next_token(self):

        while self.current_char is not None:

            if self.current_char.isspace():
                self.__skip_whitespace()
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()

            if self.current_char == ':' and self.peek() == '=':
                self.__advance()
                self.__advance()
                return Token(TokenType.ASSIGN, ':=')

            if self.current_char == ';':
                self.__advance()
                return Token(TokenType.SEMI, ';')

            if self.current_char == '.':
                self.__advance()
                return Token(TokenType.DOT, '.')

            if self.current_char.isspace():
                self.__skip_whitespace()

            if self.current_char in "0123456789.":
                return Token(TokenType.NUMBER, self.__get_number())

            if self.current_char == '+':
                self.__advance()
                return Token(TokenType.PLUS, '+')

            if self.current_char == '-':
                self.__advance()
                return Token(TokenType.MINUS, '-')

            if self.current_char == '*':
                self.__advance()
                return Token(TokenType.MUL, '*')

            if self.current_char == '/':
                self.__advance()
                return Token(TokenType.DIV, '/')

            if self.current_char == '(':
                self.__advance()
                return Token(TokenType.LPAREN, '(')

            if self.current_char == ')':
                self.__advance()
                return Token(TokenType.RPAREN, ')')

            raise Exception("Unhandled Character - " + self.current_char)
        return Token(TokenType.EOF, None)

    def __skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.__advance()

    def __get_number(self):
        result = ''
        while self.current_char is not None and self.current_char in "0123456789.":
            result += self.current_char
            self.__advance()
        return result

    # peek at next token without consuming it
    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def __advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def _id(self):
        """Handle identifiers and reversed keywords"""
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.__advance()

        result = result.upper()
        token = RESERVED_KEYWORDS.get(result, Token(TokenType.ID, result))
        return token


def run_program(program):
    print("expression", program)
    tokenizer = Tokenizer(program)
    tokens = tokenizer.get_tokens()
    print("tokens")
    print(*tokens, sep='\n')
    parser = Parser(tokens)
    ast = parser.get_parsed_tree()
    solver = Solver()
    symbol_table = solver.solve(ast)
    print(symbol_table)
    return symbol_table


# tests = [
#     ["1 + 1", 2],
#     ["8/16", 0.5],
#     ["3 -(-1)", 4],
#     ["2 + -2", 0],
#     ["10- 2- -5", 13],
#     ["(((10)))", 10],
#     ["3 * 5", 15],
#     ["-7 * -(6 / 3)", 14]
# ]
#
# for test in tests:
#     Test.assert_equals(calc(test[0]), test[1])

program = """
BEGIN
    begin
        number := 2;
        a := numBer;
        b := 10 * a + 10 * NUMBER / 4;
        c := a - -b;
        e := 8 DIV 4;
        _num := 5
    EnD;
    X := 11
END.
"""

run_program(program)
