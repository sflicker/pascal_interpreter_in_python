import enum



class DataType(enum.Enum):
    INTEGER = "Integer"
    REAL = "Real"
    STRING = "String"
    CHAR = "Char"
    BOOLEAN = "Boolean"
    ARRAY = "Array"
    RECORD = "Record"
    ENUM = "Enum"
    TEXT = "Text"
    SET = "Set"
    POINTER = "Pointer"

    def __eq__(self, other):
        return self.name == other.name
