#!/usr/bin/env python3
from enum import Enum

TOP_LEVEL_ACTION = Enum("answer_summons", "process_pms", "be_sentinel")
ACTION = Enum("roll_table")


class ActionStack:
    def __init__(self):
        pass

    def add(self, descriptor, *arguments):
        pass

    def do(self):
        pass

    def pop(self):
        pass
