import enum

class TokenType(enum.Enum):
    PROGRAM = "program"
    PROCEDURE = "procedure"
    VAR = "var"
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    LPAREN = "("
    RPAREN = ")"
    DOT = "."
    SEMI = ";"
    ASSIGN = ":="
    COLON = ":"
    COMMA = ","
    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'
    EQUAL = "="
    GREATER = ">"
    LESS = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    NOT_EQUAL = "<>"
    AND = "and"
    OR = "or"
    NOT = "not"
    INTEGER = "integer"
    REAL = "real"
    INTEGER_CONST = "integer_const"
    REAL_CONST = "real_const"
    STRING = "string"
    STRING_CONST = "string_const"
    INTEGER_DIV = "div"
    REAL_DIV = "/"
    MOD = "mod"
    BEGIN = "begin"
    END = "end"
    ID = "identifier"
    INPUT = "input"
    OUTPUT = "output"
    IF = "if"
    THEN = "then"
    ELSE = "else"
    WHILE = "while"
    DO = "do"
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
    'PROGRAM': Token(TokenType.PROGRAM, 'PROGRAM'),
    'PROCEDURE': Token(TokenType.PROCEDURE, 'PROCEDURE'),
    'VAR': Token(TokenType.VAR, 'VAR'),
    'BEGIN': Token(TokenType.BEGIN, 'BEGIN'),
    'END': Token(TokenType.END, 'END'),
    'DIV': Token(TokenType.INTEGER_DIV, 'DIV'),
    'INTEGER': Token(TokenType.INTEGER, 'INTEGER'),
    'REAL': Token(TokenType.REAL, 'REAL'),
    'STRING': Token(TokenType.STRING, 'STRING'),
    'WRITELN': Token(TokenType.OUTPUT, 'WRITELN'),
    'WRITE': Token(TokenType.OUTPUT, 'WRITE'),
    'READLN': Token(TokenType.INPUT, 'READLN'),
    'READ': Token(TokenType.INPUT, 'READ'),
    'IF': Token(TokenType.IF, "IF"),
    'THEN': Token(TokenType.THEN, "THEN"),
    'ELSE': Token(TokenType.ELSE, "ELSE"),
    'WHILE': Token(TokenType.WHILE, "WHILE"),
    'DO': Token(TokenType.DO, "DO"),
    'MOD': Token(TokenType.MOD, "MOD"),
    'AND': Token(TokenType.AND, "AND"),
    'OR': Token(TokenType.OR, "OR"),
    'NOT': Token(TokenType.NOT, 'NOT')

}



class Tokenizer(object):
    """Tokenizer accepts a text expression and returns a list of tokens"""

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.sng_opers = [TokenType.PLUS.value, TokenType.SEMI.value,
                                     TokenType.MINUS.value, TokenType.MUL.value, TokenType.REAL_DIV.value,
                                     TokenType.COLON.value, TokenType.COMMA.value, TokenType.LPAREN.value,
                                     TokenType.RPAREN.value, TokenType.EQUAL.value, TokenType.GREATER.value,
                                    TokenType.LESS.value, TokenType.DOT.value]

        self.multi_opers_dict = {TokenType.ASSIGN.value: TokenType.ASSIGN,
                            TokenType.GREATER_EQUAL.value: TokenType.GREATER_EQUAL,
                            TokenType.LESS_EQUAL.value: TokenType.LESS_EQUAL,
                            TokenType.NOT_EQUAL.value: TokenType.NOT_EQUAL}


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

            if self.current_char == '{':
                comment_start = self.current_char
                self.__advance()
                self.__skip_comment(comment_start)
                continue

            if self.current_char == '(' and self.peek() == '*':
                comment_start = '(*'
                self.__advance_multi(comment_start)
                self.__skip_comment(comment_start)
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()


            if self.current_char.isspace():
                self.__skip_whitespace()

            if self.current_char in [TokenType.SINGLE_QUOTE.value, TokenType.DOUBLE_QUOTE.value]:
                return self.__get_string(self.current_char)

            if self.current_char in "0123456789":
                return self.__get_number()

            op_token = self.__match_dbl_op()
            if op_token != None:
                return op_token

            if self.current_char in self.sng_opers:
                token_type = TokenType(self.current_char)
                token = Token(token_type, self.current_char)
                self.__advance()
                return token


            raise Exception("Unhandled Character - " + self.current_char)
        return Token(TokenType.EOF, None)

    def __skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.__advance()

    def __skip_comment(self, comment_start):
        if comment_start == "{":
            comment_end = "}"
        elif comment_start == "(*":
            comment_end = ")"
        else:
            raise Exception("Illegal comment start")
        while self.current_char != comment_end:
            self.__advance()
        self.__advance_multi(comment_end)

    def __match_dbl_op(self):

        next_two = self.current_char + self.peek()
        token_type = self.multi_opers_dict.get(next_two)
        if token_type:
            self.__advance()
            self.__advance()
            return Token(token_type, next_two)
        return None

    def __get_string(self, matching_symbol):
        """return a string. Support both single and double quotes"""
        result = ''
        self.__advance()
        while self.current_char is not matching_symbol:
            result += self.current_char
            self.__advance()
        self.__advance()
        return Token(TokenType.STRING_CONST, result)

    def __get_number(self):
        """Return a (multidigit) integer or float consumed from input"""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.__advance()

        if self.current_char == '.':
            result += self.current_char
            self.__advance()

            while (
                self.current_char is not None and
                self.current_char.isdigit()
            ):
                result += self.current_char
                self.__advance()

            token = Token(TokenType.REAL_CONST, float(result))
        else:
            token = Token(TokenType.INTEGER_CONST, int(result))

        return token

    # peek at next token without consuming it
    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def __advance_multi(self, multi_token):
        for i in range(len(multi_token)):
            self.__advance()

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
