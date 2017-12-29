#!/usr/bin/env python3
from classes.rollers.roll import Roll


def display_roll(roll: Roll):
    low, mid, high = roll.get_drop_groups()

    s_low = "" if not low else "({}) ".format(" ".join(str(v) for v in low))
    s_mid = " ".join(str(v) for v in mid)
    s_high = "" if not high else " ({})".format(" ".join(str(v) for v in high))

    return "[{}{}{}] -> {}".format(s_low, s_mid, s_high, roll.value())
