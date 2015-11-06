#!/usr/bin/env python3
from classes.tables import Table
from classes.utils.text import Text


def identify_tables(text: Text) -> list:
    """Returns a (possibly empty) list of table locations and type (start line, length, type)"""
    pass


# TODO: Properly enum-ify this
class TableType(object):
    ENUMERATED = 0
    INLINE = 1
    WIDE = 2


def parse_table(text_block: Text, table_type: TableType) -> Table:
    """Top-level parsing delegation"""
    if table_type == TableType.ENUMERATED:
        return parse_enumerated_table(text_block)
    if table_type == TableType.INLINE:
        return parse_inline_table(text_block)
    if table_type == TableType.WIDE:
        return parse_wide_table(text_block)
    raise Exception()


def parse_inline_table(text_block: Text) -> Table:
    pass


def parse_wide_table(text_block: Text) -> Table:
    pass


def parse_enumerated_table(text_block: Text) -> Table:
    pass
