from enum import Enum


class ARType(Enum):
    PROGRAM = 'PROGRAM'
    PROCEDURE = 'PROCEDURE'
    FUNCTION = 'FUNCTION'

class ActivationRecord:
    def __init__(self, name, ar_type, nesting_level, parent_ar=None):
        self.name = name
        self.ar_type = ar_type
        self.nesting_level = nesting_level
        self.parent_ar = parent_ar
        self.members = {}

    def __setitem__(self, key, value):
        self.members[key] = value

    def __getitem__(self, key):
        return self.members[key]

    def get(self, key):
        return self.members.get(key)

    def __str__(self):
        lines = [
            '{level}: {ar_type} {name}'.format(
                level=self.nesting_level,
                ar_type=self.ar_type.value,
                name=self.name,
            )
        ]
        for name, val in self.members.items():
            lines.append(f'    {name:<20}: {val}')

        s = '\n'.join(lines)
        return s

    def __repr__(self):
        return self.__str__()