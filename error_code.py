from aenum import MultiValueEnum
class ErrorCode(MultiValueEnum):
    UNEXPECTED_TOKEN = 'Unexpected Token', 100
    ID_NOT_FOUND = 'Identifier not found', 101
    DUPLICATE_ID = 'Duplicate id found', 102
    INCORRECT_NUM_OF_ARGS = "Incorrect Number of Arguments", 103
    FUNCTION_MUST_RETURN_TYPE = "Function must have a return type", 104
    UNKNOWN_ERROR = "Unknown Error", 105
    EXPECTED_IDENTIFIER = "Expected Identifier", 106
    TYPE_ERROR = "Type Error", 107
    INVALID_OPERATION = "Invalid Operation", 108

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
