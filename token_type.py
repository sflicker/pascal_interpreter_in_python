import enum

class TokenType(enum.Enum):
    # single - character token types
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    REAL_DIV = "/"
    LPAREN = "("
    RPAREN = ")"
    DOT = "."
    SEMI = ";"
    COLON = ":"
    COMMA = ","
    EQUAL = "="
    GREATER = ">"
    LESS = "<"
    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'
    #multi character ops
    ASSIGN = ":="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    NOT_EQUAL = "<>"
    #reserved words - must begin with PROGRAM
    PROGRAM = "PROGRAM"
    PROCEDURE = "PROCEDURE"
    VAR = "VAR"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    INTEGER = "INTEGER"
    REAL = "REAL"
    STRING = "STRING"
    INTEGER_DIV = "DIV"
    MOD = "MOD"
    BEGIN = "BEGIN"
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    IF = "IF"
    THEN = "THEN"
    ELSE = "ELSE"
    WHILE = "WHILE"
    DO = "DO"
    END = "END"
    # end of reserved words - must end with END
    # misc
    ID = "IDENTIFIER"
    INTEGER_CONST = "INTEGER_CONST"
    REAL_CONST = "REAL_CONST"
    STRING_CONST = "STRING_CONST"
    EOF = "EOF"


class Token(object):
    def __init__(self, type: TokenType, value: str, lineno=None, column=None):
        self.type: TokenType = type
        self.value: str = value
        self.lineno = lineno
        self.column = column

    def __str__(self):
        return "Token({type}, {value}, position={lineno}:{column})".format(
            type=self.type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column
        )

    def __repr__(self):
        return self.__str__()


# RESERVED_KEYWORDS = {
#     'PROGRAM': Token(TokenType.PROGRAM, 'PROGRAM'),
#     'PROCEDURE': Token(TokenType.PROCEDURE, 'PROCEDURE'),
#     'VAR': Token(TokenType.VAR, 'VAR'),
#     'BEGIN': Token(TokenType.BEGIN, 'BEGIN'),
#     'END': Token(TokenType.END, 'END'),
#     'DIV': Token(TokenType.INTEGER_DIV, 'DIV'),
#     'INTEGER': Token(TokenType.INTEGER, 'INTEGER'),
#     'REAL': Token(TokenType.REAL, 'REAL'),
#     'STRING': Token(TokenType.STRING, 'STRING'),
#     'WRITELN': Token(TokenType.OUTPUT, 'WRITELN'),
#     'WRITE': Token(TokenType.OUTPUT, 'WRITE'),
#     'READLN': Token(TokenType.INPUT, 'READLN'),
#     'READ': Token(TokenType.INPUT, 'READ'),
#     'IF': Token(TokenType.IF, "IF"),
#     'THEN': Token(TokenType.THEN, "THEN"),
#     'ELSE': Token(TokenType.ELSE, "ELSE"),
#     'WHILE': Token(TokenType.WHILE, "WHILE"),
#     'DO': Token(TokenType.DO, "DO"),
#     'MOD': Token(TokenType.MOD, "MOD"),
#     'AND': Token(TokenType.AND, "AND"),
#     'OR': Token(TokenType.OR, "OR"),
#     'NOT': Token(TokenType.NOT, 'NOT')
#
# }

