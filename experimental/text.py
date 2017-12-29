#!/usr/bin/env python3


class Text:
    """A probably unnecessary wrapper for a \\n-delimited block of text."""
    def __init__(self, raw_text:str):
        self.raw_text = raw_text
        self.lines = [l.strip() for l in raw_text.split("\n")]

    def get_block(self, start, length):
        return self.lines[start: length + 1]
