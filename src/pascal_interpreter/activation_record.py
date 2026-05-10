from enum import Enum


class ARType(Enum):
    PROGRAM = 'PROGRAM'
    PROCEDURE = 'PROCEDURE'
    FUNCTION = 'FUNCTION'


class Reference:
    def __init__(self, ar, name):
        self.ar = ar
        self.name = name

    def get(self):
        return self.ar.get(self.name)

    def set(self, value):
        self.ar.assign_existing(self.name, value)


class ActivationRecord:
    def __init__(self, name, ar_type, nesting_level, parent_ar=None):
        self.name = name
        self.ar_type = ar_type
        self.nesting_level = nesting_level
        self.parent_ar = parent_ar
        self.members = {}
        self.member_types = {}

    def __setitem__(self, key, value):
        self.members[key] = value

    def __getitem__(self, key):
        value = self.members[key]
        if isinstance(value, Reference):
            return value.get()
        return value

    def set_new(self, var_name, var_value, data_type=None):
        self.members[var_name] = var_value
        if data_type is not None:
            self.member_types[var_name] = data_type

    def set_reference(self, var_name, target_ar, target_name, data_type=None):
        target_value = target_ar.members[target_name]
        if isinstance(target_value, Reference):
            self.members[var_name] = target_value
        else:
            self.members[var_name] = Reference(target_ar, target_name)
        if data_type is not None:
            self.member_types[var_name] = data_type

    def assign_existing(self, var_name, new_value):
        ar = self
        while ar is not None:
            if ar.contains(var_name) is True:
                current_value = ar.members[var_name]
                if isinstance(current_value, Reference):
                    current_value.set(new_value)
                else:
                    ar[var_name] = new_value
                return
            ar = ar.parent_ar

    def get(self, key):
        ar = self
        while ar is not None:
            if ar.contains(key) is True:
                value = ar.members.get(key)
                if isinstance(value, Reference):
                    return value.get()
                return value
            ar = ar.parent_ar

    def find_record_containing(self, key):
        ar = self
        while ar is not None:
            if ar.contains(key):
                return ar
            ar = ar.parent_ar
        return None

    def get_type(self, key):
        ar = self
        while ar is not None:
            if key in ar.member_types:
                return ar.member_types[key]
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
            if isinstance(val, Reference):
                val = val.get()
            lines.append(f'    {name:<20}: {val}')

        s = '\n'.join(lines)
        return s

    def __repr__(self):
        return self.__str__()
