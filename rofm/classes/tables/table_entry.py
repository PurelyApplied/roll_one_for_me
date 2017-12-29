#!/usr/bin/env python3


class TableEntry:
    def __init__(self, content: str, *links):
        """A single possible outcome for a table, with link(s) to other table(s) if the outcome requires."""
        self.content = content
        self.table_links = list(links)


def parse_table_entry(text):
    pass
