from enum import Enum, unique, auto


@unique
class Keep(Enum):
    ALL = auto()
    TOP = auto()
    BOTTOM = auto()

    @staticmethod
    def from_char(c) -> Enum:
        if c == '':
            return Keep.ALL
        if c == '^':
            return Keep.TOP
        if c.lower() == 'v':
            return Keep.BOTTOM
        raise ValueError("Cannot get Keep enum from characters other than '', '^', 'v'")

    def to_char(self) -> str:
        if self == Keep.ALL:
            return ''
        if self == Keep.TOP:
            return '^'
        if self == Keep.BOTTOM:
            return 'v'
