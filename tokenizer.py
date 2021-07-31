from error_code import LexerError
from token_type import TokenType, Token

class Tokenizer(object):
    """Tokenizer accepts a text expression and returns a list of tokens"""

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.pos: int = 0
        self.current_char: str = self.text[self.pos]
        self.lineno = 1
        self.column = 1
        self.digits = range(10)
        self.single_char_operators: list[Token] = [TokenType.PLUS.value, TokenType.SEMI.value,
                                                   TokenType.MINUS.value, TokenType.MUL.value, TokenType.REAL_DIV.value,
                                                   TokenType.COLON.value, TokenType.COMMA.value, TokenType.LPAREN.value,
                                                   TokenType.RPAREN.value, TokenType.EQUAL.value, TokenType.GREATER.value,
                                                   TokenType.LESS.value, TokenType.DOT.value, TokenType.LEFT_BRACKET.value,
                                                   TokenType.RIGHT_BRACKET.value]

        self.multi_char_operators_dict: dict = {TokenType.ASSIGN.value: TokenType.ASSIGN,
                                                TokenType.GREATER_EQUAL.value: TokenType.GREATER_EQUAL,
                                                TokenType.LESS_EQUAL.value: TokenType.LESS_EQUAL,
                                                TokenType.NOT_EQUAL.value: TokenType.NOT_EQUAL}
        self.reserved_keywords = self._build_reserved_keywords()

    def error(self):
        s = "Lexer error on '{lexeme}' line: {lineno} column: {column}".format(
            lexeme = self.current_char,
            lineno = self.lineno,
            column = self.column
        )
        raise LexerError(message=s)

    def _build_reserved_keywords(self):
        """Build a dictionary of reserved keywords.

        The function relies on the fact that in the TokenType
        enumeration the beginning of the block of reserved keywords
        is marked with PROGRAM and the end of the block is marked with
        the END keyword."""

        tt_list = list(TokenType)
        start_index = tt_list.index(TokenType.PROGRAM)
        end_index = tt_list.index(TokenType.END)
        reserved_keywords = {
            token_type.value: token_type for token_type in tt_list[start_index:end_index + 1]
        }
        return reserved_keywords

    """Return a list of tokens"""

    def get_tokens(self) -> list[Token]:
        tokens: list = []
        while self.current_char is not None:
            token = self.__get_next_token()
            tokens.append(token)

        tokens.append(Token(TokenType.EOF, ""))
        return tokens

    def __get_next_token(self) -> Token:

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
                return self.__get_string_token(self.current_char)

            if self.current_char in "0123456789":
                return self.__get_number_const()

            op_token = self.__match_dbl_op()
            if op_token is not None:
                return op_token

            if self.current_char in self.single_char_operators:
                token_type = TokenType(self.current_char)
                token = Token(token_type, self.current_char, self.lineno, self.column)
                self.__advance()
                return token


            self.error()
        return Token(TokenType.EOF, None)

    def __set_pos(self, token: Token):
        token.lineno = self.lineno
        token.column = self.column
        return token

    def __skip_whitespace(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self.__advance()

    def __skip_comment(self, comment_start: str) -> None:
        if comment_start == "{":
            comment_end = "}"
        elif comment_start == "(*":
            comment_end = ")"
        else:
            self.error()
        while self.current_char != comment_end:
            self.__advance()
        self.__advance_multi(comment_end)

    def __match_dbl_op(self) -> Token:

        peek_char = self.peek()
        if peek_char is not None:
            next_two = self.current_char + peek_char
            token_type = self.multi_char_operators_dict.get(next_two)
            if token_type:
                self.__advance()
                self.__advance()
                return Token(token_type, next_two, self.lineno, self.column)
        return None

    def __get_string_token(self, matching_symbol: str) -> Token:
        """return a string. Support both single and double quotes"""
        result = ''
        self.__advance()
        while self.current_char is not matching_symbol:
            result += self.current_char
            self.__advance()
        self.__advance()
        return Token(TokenType.STRING_CONST, result, self.lineno, self.column)

    def __get_number_const(self) -> Token:
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

        return self.__set_pos(token)

    # peek at next token without consuming it
    def peek(self) -> str:
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def __advance_multi(self, multi_token) -> None:
        for i in range(len(multi_token)):
            self.__advance()

    def __advance(self) -> None:
        if self.current_char == '\n':
            self.lineno += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            self.column += 1

    def _id(self) -> Token:
        """Handle identifiers and reversed keywords"""
        #create new token
        token = Token(type=None, value=None, lineno=self.lineno, column=self.column)
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.__advance()

        result = result.upper()
        token_type = self.reserved_keywords.get(result)
        if token_type is None:
            token.type = TokenType.ID
            token.value = result
        elif token_type in [TokenType.TRUE, TokenType.FALSE]:
            token.type = TokenType.BOOLEAN_CONST
            token.value = result
        else:
            token.type = token_type
            token.value = result

        return token


