#!/usr/bin/env python3
import random
import re

from .keep import Keep

ROLL_REGEX_STR = r"(\d+)?[dD](\d+)(?:([v^])(\d+))?"
ROLL_REGEX = re.compile(ROLL_REGEX_STR)
STARTS_WITH_ROLL_REGEX = re.compile(r"^" + ROLL_REGEX_STR)


class Roll(list):
    """Wrapped list of values rolled, given a roll string, i.e. 5d4 or 4d6^3"""

    maximum_dice = 100
    maximum_die_size = 1000

    def __init__(self, s: str, sort_by=None):
        self.original_string = s
        match = ROLL_REGEX.match(s)

        self.n = int(match.group(1)) if match.group(1) is not None else 1
        self.k = int(match.group(2))
        drop = match.group(3)
        keep_str = match.group(4)
        self.keep = drop and Keep.from_char(drop) or Keep.ALL
        self.keep_count = self.n if not drop else int(keep_str)

        self._validate()

        super().__init__(random.randint(1, self.k) for _ in range(self.n))
        self.sort(key=sort_by)

    def reroll(self):
        super().__init__(random.randint(1, self.k) for _ in range(self.n))

    def min(self):
        return self.keep_count

    def max(self):
        return self.k * self.keep_count

    def __repr__(self):
        return "Roll('{}')".format(self.original_string)

    def __str__(self):
        if self.n == 1:
            return str(self.value())

        start, end = self._get_sections()
        bottom_dropped_dice = wrap_in_parens_if_not_empty(_join_to_string(self, 0, start), pad_after=" ")
        kept_dice = _join_to_string(self, start, end)
        top_dropped_dice = wrap_in_parens_if_not_empty(_join_to_string(self, end, len(self)), pad_before=" ")

        return "[{}{}{}] -> {}".format(
            bottom_dropped_dice,
            kept_dice,
            top_dropped_dice,
            self.value())

    def _get_sections(self):
        """Returns indices defining the range of dice kept.
        e.g., 4d6^3 -> [1, 4, 5, 6] will return the tuple (1, 4)"""
        start = 0 if self.keep != Keep.TOP else len(self) - self.keep_count
        end = len(self) if self.keep != Keep.BOTTOM else self.keep_count
        return start, end

    def value(self):
        return sum(self[i] for i in range(*self._get_sections()))

    def _validate(self):
        if not 0 < self.keep_count <= self.n:
            raise TypeError("Roll string '{}' would keep an invalid number of dice.".format(self.original_string))
        if not 0 < self.n <= self.maximum_dice:
            raise TypeError("Number of dice [{}] is not between 0 and maximum dice limit [{}]".format(
                self.n, self.maximum_dice))
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
        return eval(self.format_string.format(*(roll.min() for roll in self.rolls)))

    def max(self):
        # TODO: This doesn't take - or / into account
        if '-' in self.original_string or '/' in self.original_string:
            raise ArithmeticError("Throw.max does not take sensible things into account.")
        return eval(self.format_string.format(*(roll.max() for roll in self.rolls)))

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
    return "" if not s else "{}({}){}".format(pad_before, s, pad_after)
