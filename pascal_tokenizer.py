import enum

class TokenType(enum.Enum):
    PROGRAM = "program"
    PROCEDURE = "procedure"
    VAR = "var"
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    LPAREN = "{"
    RPAREN = "}"
    DOT = "."
    SEMI = ";"
    ASSIGN = ":="
    COLON = ":"
    COMMA = ","
    SINGLE_QUOTE = "'"
    INTEGER = "integer"
    REAL = "real"
    INTEGER_CONST = "integer_const"
    REAL_CONST = "real_const"
    STRING = "string"
    STRING_CONST = "string_const"
    INTEGER_DIV = "div"
    REAL_DIV = "/"
    BEGIN = "begin"
    END = "end"
    ID = "identifier"
    WRITELN = "writeln"
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
    'WRITELN': Token(TokenType.WRITELN, 'WRITELN')
}



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

            if self.current_char == '{':
                self.__advance()
                self.__skip_comment()
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

            if self.current_char == TokenType.SINGLE_QUOTE.value:
                return self.__get_string()

            if self.current_char in "0123456789.":
                return self.__get_number()

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
                return Token(TokenType.REAL_DIV, '/')

            if self.current_char == ':':
                self.__advance()
                return Token(TokenType.COLON, ':')

            if self.current_char == ',':
                self.__advance()
                return Token(TokenType.COMMA, ',')

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

    def __skip_comment(self):
        while self.current_char != '}':
            self.__advance()
        self.__advance();

    def __get_string(self):
        result = ''
        self.__advance()
        while self.current_char is not TokenType.SINGLE_QUOTE.value:
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
