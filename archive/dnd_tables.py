"""Class definitions for Table and associate objects"""

import logging
import re
from string import punctuation, whitespace

from archive.dice import Roll

# Slightly lower roll debugging for cleaner debug logs at standard
# level.  It is considered bad form to make these custom logging
# levels.
ROLL_DEBUG_LEVEL = logging.DEBUG - 1


# TODO: Allow columned "wide" tables:
# | Outcome | T1  | T2 |
# |:--      |:--  |:-- |
# |  1      | O1a | O1b|
# |  2      | O2a | O2b|


class TableParsingError(RuntimeError):
    pass


class TableSource:
    def __init__(self, text):
        logging.debug("Building TableSource.")
        self.lines = [l.strip() for l in text.split("\n") if l.strip()]
        self.tables = []
        logging.debug("Begin TableSource parsing."
                      "  For full details, lower logging level to"
                      " ROLL_DEBUG_LEVEL={}.".format(ROLL_DEBUG_LEVEL))
        self._parse()

    def __bool__(self):
        return bool(self.tables)

    def __repr__(self):
        return "<TableSource>"

    def _parse(self):
        table_ranges = self.identify_table_ranges()
        self.tables = [Table("\n".join(self.lines[start:stop]))
                       for start, stop in table_ranges]

    def identify_table_ranges(self):
        logging.log(ROLL_DEBUG_LEVEL, "Identify table ranges...")
        table_ranges = []
        line_number = 0
        while line_number < len(self.lines):
            # logging.debug("Line {} of {}...".format(line_number, len(self.lines)))
            line = self.lines[line_number]
            # If the line starts with a die-roll...
            if re.search(r"^[0-9 ]*d\s*[0-9]+[0-9v^ ]",
                         line.strip(punctuation + whitespace)):
                logging.log(ROLL_DEBUG_LEVEL,
                            "Possible die line: {}".format(line.strip()))
                start = line_number
                stop = line_number + 1
                while (stop < len(self.lines)
                       and re.search(r"^[0-9]",
                                     self.lines[stop].lstrip(punctuation + whitespace))):
                    stop += 1
                table_ranges.append((start, stop))
                line_number = stop - 1
            line_number += 1
        return table_ranges

    def print_all_tables(self):
        return "\n\n".join(str(t) for t in self.tables)


class Table:
    """Container for a single set of TableItem objects
    A single post will likely contain many Table objects"""

    def __init__(self, text=''):
        super(Table, self).__init__()
        self.text = text
        self.dice = None
        self.dice_range = None
        self.header = "NIL"
        # Should I be using a dictionary instead?  It would be
        # cleaner, but would make tables that are numbered just with
        # 1s harder to parse.
        self.outcomes = []
        self._last_roll_result = None
        self._last_roll_explicit = None
        if text:
            self._parse()

    def __repr__(self):
        return "<Table: {}>".format(self.header)

    def __str__(self):
        if self._last_roll_explicit is None:
            self.roll()
        ret_str = "{}...    \n{}    \n{}".format(
            self.header.strip(punctuation + whitespace),
            self._last_roll_explicit,
            self.outcomes[self._last_roll_result].strip(punctuation + whitespace))
        return ret_str

    def _parse(self):
        logging.log(ROLL_DEBUG_LEVEL, "Parsing table...")
        lines = [l.strip() for l in self.text.split('\n') if l.strip()]
        head = lines.pop(0)
        logging.log(ROLL_DEBUG_LEVEL, "Table head: {}".format(head.strip()))
        regex = re.search("^([0-9dv^ ]+)(.*)",
                          head.lstrip(punctuation))
        roll_string = regex.group(1).strip()
        if not roll_string:
            logging.error(
                "Could not determine die in header line: {}".format(
                    head.strip()))
            raise TableParsingError("TableParsingError - bad die.")
        self.header = regex.group(2).strip(punctuation + whitespace)
        self.dice = Roll(roll_string.strip())
        self.dice_range = self.dice.get_range()
        # Pad the bottom with None, probably only one entry, for
        # index-access later.
        self.outcomes = [None] * self.dice_range[0]
        for line in lines:
            if not line.strip(punctuation + whitespace):
                continue
            line_regex = re.search(r"^([0-9]+)[-—– ]*([0-9]*)(.*)", line)
            start_str, stop_str, outcome = line_regex.groups()
            outcome = outcome.strip(punctuation + whitespace)
            start = int(start_str)
            stop = int(stop_str) if stop_str else start
            weight = stop - start + 1
            self.outcomes.extend([outcome] * weight)
        if len(self.outcomes) != self.dice_range[1] + 1:
            logging.warning("Table outcome mismatch expected range.")

    def roll(self):
        logging.log(ROLL_DEBUG_LEVEL,
                    "Rolling table: {}".format(self.header))
        self.dice.roll()
        self._last_roll_result = int(self.dice)
        logging.log(ROLL_DEBUG_LEVEL,
                    " Roll value: {}".format(self._last_roll_result))
        self._last_roll_explicit = str(self.dice)
        logging.log(ROLL_DEBUG_LEVEL,
                    " Roll explicit: {}".format(self._last_roll_explicit))
        return self.outcomes[self._last_roll_result]


class WideTable(Table):
    """Work in progress; not yet useful.  Should contain a list of
tables?"""

    def __init__(self, text):
        super(WideTable, self).__init__(text)
        # The roll column is essentially stripped in Table's parser
        self.width = len(self.header.split("|")) - 1
        self.tables = []
        for i in range(self.width):
            # But the roll column wouldn't have been removed from the
            # header
            head = self.header.split("|")[i + 1]
            outs = [None] + [out.split("|")[i] for out in self.outcomes[1:]]
            t = Table()
            t.header = head
            t.outcomes = outs
            t.dice = self.dice
            t.dice_range = self.dice_range
            t.roll()
            self.tables.append(t)

    def __str__(self):
        return "\n\n".join(str(t) for t in self.tables)

    def __repr__(self):
        return "<WideTable>"


# Needs reimplementation
class InlineTable(Table):
    def _parse(self):
        pass
