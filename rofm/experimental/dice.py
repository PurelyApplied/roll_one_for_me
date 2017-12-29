"""A dice parser that is more cumbersome but more responsive than the
module available in pypi.dice"""

import logging
import operator
import random

_OPERATOR_MAP = {"+": operator.add,
                 "-": operator.sub,
                 "*": operator.mul,
                 "/": operator.floordiv}

_OP_TO_STR = {op: char for char, op in _OPERATOR_MAP.items()}

# Regex for a single die roll
REGEX = r"\d*\s*d\s*\d+(?:\s*[v^]\s*\d+)?"


class SimpleRoll:
    """At most {n=1}dK{[v^][L=K]}
    For instance:
    d5, 2d5, 4d5v2.
    Class members 'max_n', 'max_k' limit permissible roll sizes."""

    maximum_dice = 100
    maximum_die_size = 1000
    history_length = 10

    @classmethod
    def set_maximum_dice(cls, n):
        assert n > 0, "Cannot set maximum dice to a non-positive number."
        cls.maximum_dice = n

    @classmethod
    def set_maximum_die_size(cls, m):
        assert m > 0, "Cannot set maximum die size to a non-positive number."
        cls.maximum_die_size = m

    @classmethod
    def set_history_length(cls, h):
        assert h > 0, "Cannot set dice history length a non-positive number."
        cls.maximum_dice = h

    def __init__(self, input_string):
        logging.debug("Initialize SimpleRoll")
        # Allocate
        self.n = None
        self.k = None
        self.l = None
        self.value = None
        self.last_roll = None

        logging.debug("Generating SimpleRoll from input string: {}".format(input_string))
        # Make sure it's a roll to begin with
        if "d" not in input_string.lower():
            logging.error("RollParsingError")
            raise RollParsingError("SimpleRoll received non-roll string.")
        # Purge whitespace, get numbers
        self.string = input_string.replace(" ", "").lower()
        count, tail = self.string.split("d")
        self.n = int(count) if count else 1
        self.k = (
            int(tail)
            if not self._limiting()
            else int(tail.split(self._limiting())[0]))
        self.l = (
            self.n
            if not self._limiting()
            else int(tail.split(self._limiting())[1]))
        # sanity:
        self._sanity()
        self.history = []
        self.roll()
        logging.debug("Roll generated: {}".format(self))

    def __repr__(self):
        return "<SimpleRoll: {}>".format(self.string)

    def __str__(self):
        if self.n == 1:
            return "[d{}] -> {}".format(self.k, self.last_roll[0])
        if not self._limiting():
            return "[{}: {}] -> {}".format(
                self.string,
                " ".join(str(v) for v in self.last_roll),
                self.value)
        elif self._limiting() == "v":
            return "[{}: {} ({})] -> {}".format(
                self.string,
                " ".join(str(v) for v in self.last_roll[:self.l]),
                " ".join(str(v) for v in self.last_roll[self.l:]),
                self.value)
        else:
            return "[{}: ({}) {}] -> {}".format(
                self.string,
                " ".join(str(v) for v in self.last_roll[:-self.l]),
                " ".join(str(v) for v in self.last_roll[-self.l:]),
                self.value)

    def __int__(self):
        return self.value

    def _sanity(self):
        if self.l <= 0:
            logging.error("RollLimitError - kept <= 0")
            raise RollLimitError("SimpleRoll to keep non-positive dice count.")
        if self.n <= 0:
            logging.error("RollLimitError - dice count <= 0")
            raise RollLimitError("SimpleRoll to roll non-positive dice count.")
        if self.k <= 1:
            logging.error("RollLimitError - die face <= 1")
            raise RollLimitError("SimpleRoll die face must be at least two.")
        if self.l > self.n:
            logging.error("RollLimitError - kept > count")
            raise RollLimitError("SimpleRoll to keep more dice than present.")
        if self.n > SimpleRoll.maximum_dice:
            logging.error(
                "RollLimitError - dice limit ({})".format(SimpleRoll.maximum_dice))
            raise RollLimitError("SimpleRoll exceeds maximum allowed dice.")
        if self.k > SimpleRoll.maximum_die_size:
            logging.error(
                "RollLimitError - die face limit ({})".format(SimpleRoll.maximum_die_size))
            raise RollLimitError("SimpleRoll exceeds maximum allowed die face.")

    def _limiting(self):
        """Returns "^", "v", or "" when "^", "v", or neither are present in the generating string, respectively."""
        if "^" in self.string:
            return "^"
        if "v" in self.string:
            return "v"
        return ""

    def get_range(self):
        """Returns tuple (low, high) of the lowest and highest possible rolls"""
        return self.l, self.l * self.k

    def roll(self):
        self.last_roll = sorted([random.randint(1, self.k)
                                 for _ in range(self.n)])
        if self.n == self.l:
            self.value = sum(self.last_roll)
        elif "^" in self.string:
            self.value = sum(self.last_roll[-self.l:])
        elif "v" in self.string:
            self.value = sum(self.last_roll[:self.l])
        else:
            raise RuntimeError("SimpleRoll l != n, but without v or ^")
        return self.value


# noinspection PyTypeChecker
class Roll:
    """A roll consists of one or more SimpleRoll instances, separated by
operators +-*/.  Mathematical priority of */ are respected, but
parentheses are not permitted.  All operations are performed with
left-to-right implicit associativity.  Division is performed as
integer division.

Class member 'max_compound_roll_length' limits the number of die
predicates allowed.
    """

    max_compound_roll_length = 20

    @classmethod
    def set_max_roll_length(cls, max_len=20):
        cls.max_compound_roll_length = max_len

    def __init__(self, input_string):
        logging.debug(
            "Generating Roll from input string: {}".format(input_string))
        self.string = input_string.replace(" ", "").lower()
        self.items = []
        self.value = None
        # Begin parsing
        self._parse()
        self.evaluate()
        logging.debug("Simple roll generated: {}".format(self))

    def __repr__(self):
        return "<Roll: {}>".format(self.string)

    def __str__(self):
        if len(self.items) == 1:
            return str(self.items[0])
        return "[({}){}] -> {}".format(
            str(self.items[0]),
            "".join(
                " {} ({})".format(
                    str(self.items[i]),
                    str(self.items[i + 1]))
                for i in range(1, len(self.items), 2)),
            self.value)

    def __int__(self):
        return self.value

    def _parse(self):
        logging.debug("Parsing Roll...")
        # Identify operator positions:
        ops = [(i, s) for i, s in enumerate(self.string) if s in '*/+-']
        logging.debug("Operators: {}".format(ops))
        if len(ops) // 2 >= Roll.max_compound_roll_length:
            logging.error("RollLimitError - predicate length")
            raise RollLimitError(
                "Roll exceeds maximum predicate length ({}).".format(
                    Roll.max_compound_roll_length))
        logging.debug("Building items...")
        # Kind of awkward, but too many boundary cases otherwise
        # Allocate space
        self.items = [None] * (2 * len(ops) + 1)
        # Inject operators
        self.items[1::2] = [o for _, o in ops]
        logging.debug("Items: {}".format(self.items))
        # Update index ranging
        starts = [0] + [i + 1 for i, _ in ops]
        stops = [i for i, _ in ops] + [len(self.string)]
        self.items[::2] = [self.string[start:stop]
                           for start, stop in zip(starts, stops)]
        logging.debug("Items: {}".format(self.items))
        # Convert to SimpleRolls
        logging.debug("Converting to odd indexed items to SimpleRoll...")
        for i, v in enumerate(self.items):
            # operators stay as operator strings
            if not i % 2:
                self.items[i] = (int(v)
                                 if v.isnumeric()
                                 else SimpleRoll(v))

    def evaluate(self):
        self.value = self._do_basic_math([int(v)
                                          if not i % 2
                                          else _OPERATOR_MAP[v]
                                          for i, v in enumerate(self.items)])

    def roll(self):
        for item in self.items:
            if isinstance(item, SimpleRoll):
                item.roll()
        self.evaluate()
        return int(self)

    def get_range(self):
        ranges = [v.get_range()
                  if not i % 2
                  else _OPERATOR_MAP[v]
                  for i, v in enumerate(self.items)]
        low_range = [(v[0]
                      if not (i > 0 and ranges[i - 1] == operator.floordiv)
                      else v[1])
                     if not i % 2
                     else v
                     for i, v in enumerate(ranges)]
        high_range = [(v[1]
                       if not (i > 0 and ranges[i - 1] == operator.floordiv)
                       else v[0])
                      if not i % 2
                      else v
                      for i, v in ranges]
        return self._do_basic_math(low_range), self._do_basic_math(high_range)

    @staticmethod
    def _do_basic_math(values: "[int, operator, int, operator, ...]"):
        """Performs basic math operators in a list of alternating ints and
operators.  Respects priority of multiplication and division."""
        # We'll use a sanitized eval call for simplicity.  To address the
        # possible security issue, we'll be explicit about incoming
        # types.
        if len(values) % 2 != 1:
            raise BasicMathError("Malformed list in _do_basic_math")
        if not all(isinstance(v, int) for v in values[::2]):
            raise BasicMathError("Expected int in even indexed positions.")
        if not all(op in _OP_TO_STR.keys() for op in values[1::2]):
            raise BasicMathError("Expected operator in odd indexed positions.")
        as_str = [str(v)
                  if not i % 2
                  else _OP_TO_STR[v]
                  for i, v in enumerate(values)]
        total = eval("".join(as_str))
        return total


def roll(input_string):
    return Roll(input_string).roll()


def set_limits(max_n=None, max_k=None, max_predicate=None):
    SimpleRoll.set_roll_limits(max_n, max_k)
    Roll.set_max_roll_length(max_predicate)


class RollParsingError(RuntimeError):
    pass


class RollLimitError(RuntimeError):
    pass


class BasicMathError(ValueError):
    pass
