#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any

import dice


@dataclass
class Table:
    """A simple backbone for a lookup-table as dictated by a die-roll."""
    dice: str
    description: str = ''
    lookup_table: Dict[int, Any] = field(default_factory=dict)

    def __str__(self):
        return f"{self.dice} table{': ' if self.description else ''}{self.description}"

    def roll(self):
        outcome = int(dice.roll(self.dice))
        return self.get(outcome)

    def get(self, outcome):
        return self.lookup_table[outcome]

    def low(self):
        return int(dice.roll_min(self.dice))

    def high(self):
        return int(dice.roll_max(self.dice))

    def _validate(self):
        return
        # self._validate_ranges()

    def _validate_ranges(self):
        for i in range(int(dice.roll_min(self.dice)), int(dice.roll_max(self.dice)) + 1):
            assert i in self.lookup_table, f"Table is missing an entry for a '{self.dice}' outcome of {i}."


class SimpleTable(Table):
    def __init__(self, roll, items: List[Any], description=''):
        super(SimpleTable, self).__init__(roll, description=description)
        low, high = self.low(), self.high()
        self.lookup_table = {i + low: elem for i, elem in enumerate(items)}

        self._validate()


@dataclass
class WeightedTable(Table):
    outcomes: List[Any] = field(default_factory=list, repr=False)
    ranges: List[Tuple[int]] = field(default_factory=list ,repr=False)    # inclusive

    def __init__(self, roll, outcomes, ranges, description=''):
        self.outcomes = outcomes
        self.ranges = ranges

        super(WeightedTable, self).__init__(roll, description=description)
        for item, (lower_range, higher_range) in zip(self.outcomes, self.ranges):
            for i in range(lower_range, higher_range + 1):
                if i in self.lookup_table:
                    raise ValueError(f"This table would have multiple outcomes for {i}")
                self.lookup_table[i] = item

        self._validate()


if __name__ == '__main__':
    st = SimpleTable('2d4', [2, 3, 4, 5, 6, 7, 8], description="A simple 2d4 table")
    wt = WeightedTable('2d4', ["2-4", "5-6", "7-8"], [(2, 4), (5, 6), (7, 8)], description="A weighted table")
    print(wt)
