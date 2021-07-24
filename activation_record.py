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

    def set_new(self, var_name):
        self.members[var_name] = None

    def assign_existing(self, var_name, new_value):
        ar = self
        while ar is not None:
            if ar.contains(var_name) is True:
                ar[var_name] = new_value
                return
            ar = ar.parent_ar

    def get(self, key):
        ar = self
        while ar is not None:
            if ar.contains(key) is True:
                return ar.members.get(key)
            ar = ar.parent_ar

    def contains(self, key):
        return key in self.members

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