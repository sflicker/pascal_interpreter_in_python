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

    def __eq__(self, other):
        return self.name == other.name
