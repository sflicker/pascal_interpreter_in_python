from enum import Enum
class ErrorCode(Enum):
    UNEXPECTED_TOKEN = 'Unexpected Token'
    ID_NOT_FOUND = 'Identifier not found'
    DUPLICATE_ID = 'Duplicate id found'
    INCORRECT_NUM_OF_ARGS = "Incorrect Number of Arguments"
    UNKNOWN_ERROR = "Unknown Error"

class Error(Exception):
    def __init__(self, error_code=None, token=None, message=None):
        self.error_code = error_code
        self.token = token
        self.message = f'{self.__class__.__name__}: {message}'

class LexerError(Error):
    pass

class ParserError(Error):
    pass

class SemanticError(Error):
    pass
