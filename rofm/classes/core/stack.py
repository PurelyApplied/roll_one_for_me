#!/usr/bin/env python3
from enum import Enum


class Command(str, Enum):
    """This enum defines possible command strings when summoning."""
    default = "default"
    stats = "stats"


class Action(str, Enum):
    parse = "parse(target) -> table"
    roll = "roll(table)"
    add_table_to_table_set = "add_table_to_table_set(reflection, table)"


def pack(__f, *args, **kwargs):
    return __f, args, kwargs


def call(__f, args, kwargs):
    return __f(*args, **kwargs)


def unpack(package):
    assert isinstance(package, tuple) or isinstance(package, list) and len(package) == 3
    return call(*package)


class Stack(list):
    def __init__(self, *actions: "Actions listed first execute first."):
        """
        Instance members:

        self.stack contains either a tuple in the form (func, args, kwargs) or a TableAction.
        TableAction objects are popped, translated to a (func, args, kwargs) tuple, and pushed back for processing.

        """
        super().__init__(*actions[::-1])
        self.height = len(self)
        self.depth = 0

    def append(self, o):
        super().append(o)
        self.height += 1


def example_print(a, b, c, d, e, f, g):
    for char, val in zip('abcdefg', (a, b, c, d, e, f, g)):
        print("{} = {}".format(char, val))

if __name__ == '__main__':
    unpack(pack(example_print, 1, 2, 3, 4, g=9, e=5, f=100))
    stack = Stack(range(10, 0, -1))
    print(stack)
