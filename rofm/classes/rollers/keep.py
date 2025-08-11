from enum import Enum, unique


@unique
class Keep(Enum):
    ALL = 1
    TOP = 2
    BOTTOM = 3

    @staticmethod
    def from_char(c) -> Enum:
        if c == '':
            return Keep.ALL
        if c == '^':
            return Keep.TOP
        if c.lower() == 'v':
            return Keep.BOTTOM
        return None

    def to_char(self) -> str:
        if self == Keep.ALL:
            return ''
        if self == Keep.TOP:
            return '^'
        if self == Keep.BOTTOM:
            return 'v'
