#!/usr/bin/env python3
import re
from string import punctuation, whitespace
from typing import Union, Tuple

from ..rollers.roll import Roll, Throw, STARTS_WITH_ROLL_REGEX

_trash = punctuation + whitespace
_line_regex = "^(\d+)(\s*-+\s*\d+)?(.*)"


class Table:
    def __init__(self, roll: Union[str, Roll, Throw], header: str,
                 *outcomes: Union[Tuple[int, str]]):
        """:param roll: Dice generation method by which outcomes are selected
        :param header: Title of the table
        :param outcomes: List of tuples"""
        self.roll = roll if isinstance(roll, Roll) or isinstance(roll, Throw) else Throw(roll)
        self.header = header
        self.outcomes = list(outcomes)
        self.outcomes.sort()

    def __str__(self):
        return "Table({}, '{}', {})".format(self.roll.original_string, self.header, self.outcomes)

    def get_outcome(self):
        value = self.roll.value()
        return self.outcomes[value - 1]


def parse_enumerated_table(text):
    lines = text.strip('\n').split('\n')
    header_line = lines.pop(0)
    leading_header_roll = re.search(STARTS_WITH_ROLL_REGEX, header_line.strip(_trash))
    if not leading_header_roll:
        raise RuntimeError("AHHHHH!")
    roll_string = leading_header_roll.group(0)
    roll = Roll(roll_string)
    header = header_line.strip(_trash)[leading_header_roll.span()[1]:]
    outcomes = [l for l in lines if re.search(_line_regex, l.strip(_trash))]
    table = Table(roll, header, *outcomes)
    return table


def parse_inline_table(tight_inline_text):
    """:param tight_inline_text: A line *beginning* with the roll indicator"""
    # Match roll and advance
    # Match any "header" before enumeration begins
    # Match items
    return None
