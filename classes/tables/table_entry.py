#!/usr/bin/env python3


class LegacyTableItem:
    """Legacy class: This class allows simple handling of in-line subtables"""

    def __init__(self, text, w=0):
        self.text = text
        self.inline_table = None
        self.outcome = ""
        self.weight = 0

        self._parse()

        # If parsing fails, particularly in inline-tables, we may want
        # to explicitly set weights
        if w:
            self.weight = w

    def __repr__(self):
        return "<TableItem: {}{}>".format(self.outcome, "; has inline table" if self.inline_table else "")

    def _parse(self):
        main_regex = re.search(_line_regex, self.text.strip(_trash))
        if not main_regex:
            return
        # Grab outcome
        self.outcome = main_regex.group(3).strip(_trash)
        # Get weight / ranges
        if not main_regex.group(2):
            self.weight = 1
        else:
            try:
                start = int(main_regex.group(1).strip(_trash))
                stop = int(main_regex.group(2).strip(_trash))
                self.weight = stop - start + 1
            except:
                self.weight = 1
        # Identify if there is a subtable
        if re.search("[dD]\d+", self.outcome):
            die_regex = re.search("[dD]\d+", self.outcome)
            try:
                self.inline_table = InlineTable(self.outcome[die_regex.start():])
            except RuntimeError as e:
                lprint("Error in inline_table parsing ; table item full text:")
                lprint(self.text)
                lprint(e)
                self.outcome = self.outcome[:die_regex.start()].strip(_trash)
        # this might be redundant
        self.outcome = self.outcome.strip(_trash)

    def get(self):
        if self.inline_table:
            return self.outcome + self.inline_table.roll()
        else:
            return self.outcome


class TableEntry(LegacyTableItem):
    def __init__(self, content: str=None, *links):
        """A single possible outcome for a table, with link(s) to other table(s) if the outcome requires."""
        self.content = content
        self.table_links = list(links)
    # TODO: Should we allow "You receive [1d4+1[other table]]"?  Directly parse "1d4 + 1 [Other table]" inline?


class TableItem(TableEntry):
    pass
