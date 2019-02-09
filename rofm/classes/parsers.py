#!/usr/bin/env python3
import re

from rofm.classes.rollers.keep import Keep


ROLL_REGEX_STR = r"(\d+)?[dD](\d+)(?:([v^])(\d+))?"
ROLL_REGEX = re.compile(ROLL_REGEX_STR)
STARTS_WITH_ROLL_REGEX = re.compile(r"^" + ROLL_REGEX_STR)


def parse_roll_string(s):
    match = ROLL_REGEX.match(s)
    n = int(match.group(1)) if match.group(1) is not None else 1
    k = int(match.group(2))
    drop = match.group(3)
    keep_str = match.group(4)
    keep = drop and Keep.from_char(drop) or Keep.ALL
    keep_count = n if not drop else int(keep_str)
    return n, k, keep, keep_count
