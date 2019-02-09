#!/usr/bin/env python3
import random
from dataclasses import dataclass

from rofm.classes.parsers import parse_roll_string, ROLL_REGEX
from .keep import Keep


@dataclass
class RollSpec:
    n: int
    k: int
    keep = Keep.ALL
    keep_count: int = 0  # Ignored by Keep.ALL


class Roll(list):
    """Wrapped list of values rolled, given a roll string, i.e. 5d4 or 4d6^3"""

    maximum_dice_count = 100
    maximum_die_size = 1000

    @staticmethod
    def from_spec(n: int, k: int, keep=Keep.ALL, keep_count=None, sort=True):
        if keep_count is None:
            keep_count = n
        str_n = '' if n <= 1 else str(n)
        str_keep = keep.to_char() + ('' if keep_count == n else str(keep_count))
        s = f"{str_n}d{k}{str_keep}"
        return Roll(s, auto_sort=sort)

    def __init__(self, s: str, *, auto_sort=True):
        self.original_string = s
        self.auto_sort = auto_sort
        self.n, self.k, self.keep, self.keep_count = parse_roll_string(s)

        self._validate()

        self._roll()

    def _roll(self):
        super().__init__(random.randint(1, self.k) for _ in range(self.n))
        if self.auto_sort:
            self.sort()

    def reroll(self):
        self._roll()

    def minimum_possible(self):
        return self.keep_count

    def maximum_possible(self):
        return self.k * self.keep_count

    def __repr__(self):
        return "Roll('{}')".format(self.original_string)

    def __int__(self):
        return sum(self)

    def __str__(self):
        if self.n == 1:
            return str(self.value())

        # WARNING: This is predicated on the roll being sorted increasingly.
        kept_start, kept_end = self._get_kept_range()
        bottom_dropped_dice = wrap_in_parens_if_not_empty(_join_to_string(self, 0, kept_start), pad_after=" ")
        kept_dice = _join_to_string(self, kept_start, kept_end)
        top_dropped_dice = wrap_in_parens_if_not_empty(_join_to_string(self, kept_end, len(self)), pad_before=" ")

        return f"[{bottom_dropped_dice}{kept_dice}{top_dropped_dice}] -> {self.value()}"

    def _get_kept_range(self):
        """Returns indices defining the range of dice kept.
        e.g., 4d6^3 -> [1, 4, 5, 6] will return the tuple (1, 4)"""
        start = 0 if self.keep != Keep.TOP else len(self) - self.keep_count
        end = len(self) if self.keep != Keep.BOTTOM else self.keep_count
        return start, end

    def value(self):
        return sum(self[i] for i in range(*self._get_kept_range()))

    def _validate(self):
        if not 0 < self.keep_count <= self.n:
            raise TypeError("Roll string '{}' would keep an invalid number of dice.".format(self.original_string))
        if not 0 < self.n <= self.maximum_dice_count:
            raise TypeError("Number of dice [{}] is not between 0 and maximum dice limit [{}]".format(
                self.n, self.maximum_dice_count))
        if not 0 < self.k <= self.maximum_die_size:
            raise TypeError("Die size [{}] is not between 0 and maximum die size [{}]".format(
                self.k, self.maximum_die_size))


class Throw:
    """A collection of Rolls, i.e. (2d4 + 2d20v1 - 10)"""
    ACCEPTABLE_CHARS = r"0123456789vV^d+-*/ ()"
    maximum_predicates = 20

    @classmethod
    def _validate(cls, s: str):
        illegal_chars = set(char for char in s if char.lower() not in cls.ACCEPTABLE_CHARS)
        if illegal_chars:
            raise TypeError(
                "Unacceptable characters ('{}') found in Throw input string: '{}'".format(
                    "".join(illegal_chars), s))

    def __init__(self, s: str):
        self._validate(s)

        self.original_string = s
        self.rolls = []
        self.format_string = ROLL_REGEX.sub(self._add_roll_to_list_and_replace_with_string_placeholder, s)
        # This self.format_string replaces every Roll substring with r'{}',
        #  so that the values may be injected before display
        #  e.g., '{} + {} - {}'

    def __repr__(self):
        return "<Throw({})>".format(self.original_string)

    def min(self):
        # TODO: This doesn't take - or / into account
        if '-' in self.original_string or '/' in self.original_string:
            raise ArithmeticError("Throw.min does not take sensible things into account.")
        return eval(self.format_string.format(*(roll.minimum_possible() for roll in self.rolls)))

    def max(self):
        # TODO: This doesn't take - or / into account
        if '-' in self.original_string or '/' in self.original_string:
            raise ArithmeticError("Throw.max does not take sensible things into account.")
        return eval(self.format_string.format(*(roll.maximum_possible() for roll in self.rolls)))

    def get_evaluated_string(self):
        return self.format_string.format(*(roll.value() for roll in self.rolls))

    def value(self):
        return eval(self.get_evaluated_string())

    def __str__(self):
        return "[{}] -> {} = {}".format(self.original_string, self.get_evaluated_string(), self.value())

    def _add_roll_to_list_and_replace_with_string_placeholder(self, m):
        roll = Roll(m.group())
        self.rolls.append(roll)
        if len(self.rolls) > self.maximum_predicates:
            raise TypeError("Throw string '{}' has more predicates than the permitted maximum [{}]".format(
                self.original_string, self.maximum_predicates))
        return r'{}'

    def reroll(self):
        for r in self.rolls:
            r.reroll()


def _join_to_string(roll, start, end):
    return " ".join(map(str, (roll[i] for i in range(start, end))))


# noinspection SpellCheckingInspection
def wrap_in_parens_if_not_empty(s, pad_before="", pad_after=""):
    return "" if not s else f"{pad_before}({s}){pad_after}"
