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
        self.type: TokenType = type
        self.value: str = value

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

