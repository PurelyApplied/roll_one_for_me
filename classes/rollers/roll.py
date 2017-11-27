#!/usr/bin/env python3
import random
import re

from classes.rollers.keep import Keep

ROLL_REGEX_STR = r"(\d+)?[dD](\d+)(?:([v^])(\d+))?"
ROLL_REGEX = re.compile(ROLL_REGEX_STR)
STARTS_WITH_ROLL_REGEX = re.compile("^" + ROLL_REGEX_STR)


class Roll(list):
    """Wrapped list of values rolled, given a roll string, i.e. 5d4 or 4d6^3"""
    def __init__(self, s: str, sort_by=None):
        match = ROLL_REGEX.match(s)
        n = int(match.group(1)) if match.group(1) is not None else 1
        k = int(match.group(2))
        drop = match.group(3)
        keep = match.group(4)
        keep_partial = drop and Keep.from_char(drop) or Keep.ALL
        keep_count = n if not drop else int(keep)

        super().__init__(random.randint(1, k) for _ in range(n))
        self.sort(key=sort_by)

        self.keep = keep_partial
        self.keep_count = keep_count
        self.n = n
        self.k = k

        if not 0 < keep_count <= len(self):
            raise TypeError("Roll string '{}' would keep an invalid number of dice.".format(s))

    def min(self):
        return self.keep_count

    def max(self):
        return self.k * self.keep_count

    def __repr__(self):
        n = self.n if self.n > 1 else ''
        k = self.k
        keep_char = Keep.from_char(self.keep)
        keep_val = self.keep_count if keep_char else ''
        return "<Roll('{}d{}{}{}')>".format(n, k, keep_char, keep_val)

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
        start = 0 if self.keep != Keep.TOP else len(self) - self.keep_count
        end = len(self) if self.keep != Keep.BOTTOM else self.keep_count
        return start, end

    def value(self):
        return sum(self[i] for i in range(*self._get_sections()))


class Throw:
    """A collection of Rolls, i.e. (2d4 + 2d20v1 - 10)"""
    ACCEPTABLE_CHARS = r"0123456789vV^d+-*/ ()"

    @staticmethod
    def _validate(s: str):
        illegal_chars = set(char for char in s if char not in Throw.ACCEPTABLE_CHARS)
        if illegal_chars:
            raise TypeError(
                "Unacceptable characters ('{}') found in Throw input string: '{}'".format(
                    "".join(illegal_chars), s))

    def __init__(self, s: str):
        Throw._validate(s)

        self.roll_string = s
        self.rolls = []

        self.format_string = ROLL_REGEX.sub(self._add_roll_to_list_and_replace_with_string_placeholder, s)

    def __repr__(self):
        return "<Throw({})>".format(self.roll_string)

    def min(self):
        # TODO: This doesn't take - or / into account
        if '-' in self.roll_string or '/' in self.roll_string:
            raise ArithmeticError("Throw.min does not take sensible things into account.")
        return eval(self.format_string.format(*(roll.min() for roll in self.rolls)))

    def max(self):
        # TODO: This doesn't take - or / into account
        if '-' in self.roll_string or '/' in self.roll_string:
            raise ArithmeticError("Throw.max does not take sensible things into account.")
        return eval(self.format_string.format(*(roll.max() for roll in self.rolls)))

    def get_evaluated_string(self):
        return self.format_string.format(*(roll.value() for roll in self.rolls))

    def value(self):
        return eval(self.get_evaluated_string())

    def __str__(self):
        return "[{}] -> {} = {}".format(self.roll_string, self.get_evaluated_string(), self.value())

    def _add_roll_to_list_and_replace_with_string_placeholder(self, m):
        roll = Roll(m.group())
        self.rolls.append(roll)
        return r'{}'


def _join_to_string(roll, start, end):
    return " ".join(map(str, (roll[i] for i in range(start, end))))


def wrap_in_parens_if_not_empty(s, pad_before="", pad_after=""):
    return "" if not s else "{}({}){}".format(pad_before, s, pad_after)


def parser_tst(n):
    for i in range(n):
        print("4d6^3 = " + str(Roll("4d6^3")))
    for i in range(n):
        print("d20 = " + str(Roll("d20")))
    for i in range(n):
        print("10d4v7 = " + str(Roll("10d4v7")))
    for i in range(n):
        print(Throw("4d6^3 + d20 - 10d4v7 * (1d3 - 1)"))
    # Throw("System.run('rm -rf /')")

if __name__ == "__main__":
    parser_tst(10)
