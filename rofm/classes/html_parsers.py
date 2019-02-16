#!/usr/env/bin python3
from dataclasses import dataclass, field
from typing import List

import dice
from bs4 import Tag, BeautifulSoup
from praw.models import Submission, Comment
from pyparsing import ParseException, ParseFatalException

from rofm.classes.tables import Table, SimpleTable, WeightedTable

HTML_PARSER = 'html.parser'
DASHES = ('-', u'–', u'—')


@dataclass
class TableContainer:
    tables: List[Table] = field(default_factory=list)


class HtmlTableEnumerationParser(TableContainer):
    """Necessarily a single table."""
    soupy_enumerations: Tag

    possible_header: Tag
    auto_parse = False

    soupy_items: List[str] = None
    table: Table = None

    def __init__(self, soupy_enumeations: Tag, auto_parse=True):
        super(HtmlTableEnumerationParser, self).__init__()

        self.possible_header = soupy_enumeations.find_previous_sibling('p')
        self.soupy_items = soupy_enumeations.find_all('li')

        if auto_parse:
            dice_roll, desc = self._get_roll_and_dec(self.possible_header)

            table = SimpleTable(dice_roll, [item.text for item in self.soupy_items], description=desc)
            self.tables = [table]

    def _get_roll_and_dec(self, possibly_a_header):
        """If the header starts with a die roll, returns that die roll and the remaining line.
        Otherwise, returns the presumed die roll (1d<item count>) and a hopeful description."""
        stripped_and_rejoined = " ".join(possibly_a_header.stripped_strings)
        first, rest = stripped_and_rejoined.split(" ", 1)
        if string_is_die_roll(first):
            return first, rest
        else:
            return f"d{len(self.soupy_items)}", "A free-standing enumeration"


class HtmlTableTagParser(TableContainer):
    """Possibly a wide table / multiple tables."""
    soupy_table: Tag
    auto_parse = True

    soupy_items: List[str] = None

    def __init__(self, soupy_table: Tag, auto_parse=True):
        super(HtmlTableTagParser, self).__init__()
        self.soupy_table = soupy_table
        self.auto_parse = auto_parse

        if auto_parse:
            self.parse()

    def parse(self):
        self.soupy_items = self.soupy_table.find_all('tr')
        exploded = [item.find_all(('th', 'td')) for item in self.soupy_items]

        first_column = [exploded[i][0] for i, _ in enumerate(exploded)]
        maybe_roll, maybe_ranges = self.try_to_get_roll_and_weights_from_column(first_column)

        if maybe_ranges:
            for column_index, _ in enumerate(exploded[0]):
                if column_index == 0:
                    continue
                column = [exploded[i][column_index] for i, _ in enumerate(exploded)]
                column_text = [e.text for e in column]
                self.tables.append(WeightedTable(maybe_roll, column_text[1:],
                                                 maybe_ranges, description=column_text[0]))
        else:
            # The first column is maybe another table.
            pass

    @staticmethod
    def try_to_get_roll_and_weights_from_column(first_column):
        text_only = [e.text for e in first_column]
        if not string_is_die_roll(text_only[0]):
            return None, None

        roll = text_only[0]
        outcome_ranges = []
        for outcome_pseudo_range in text_only[1:]:
            validated_thingies = outcome_pseudo_range.strip().strip('.')\
                .replace(DASHES[2], DASHES[0])\
                .replace(DASHES[1], DASHES[0])\
                .split(DASHES[0])
            items = [i for i in validated_thingies if i.strip()]
            if any((not i.isnumeric() for i in items)):
                raise ValueError(f"A column of {text_only} has non-numeric weights?")
            items = [int(i) for i in items]
            if len(items) == 1:
                outcome_ranges.append((items[0], items[0]))
            elif len(items) == 2:
                outcome_ranges.append(items)
            else:
                raise ValueError(f"A column of {text_only} doesn't have a sensible weight pattern?")

        return roll, outcome_ranges


class HtmlParser(TableContainer):
    html_text: str
    auto_parse = False

    soup: BeautifulSoup = None

    soupy_table_tags: List[HtmlTableTagParser] = None
    soupy_enumeration_tags: List[HtmlTableEnumerationParser] = None

    def __init__(self, html_text: str, auto_parse=False):
        self.html_text = html_text
        self.auto_parse = auto_parse

        self.soup = BeautifulSoup(self.html_text, HTML_PARSER)

        if auto_parse:
            self.parse()
            self.tables = []
            for table_tag in self.soupy_table_tags:
                self.tables.extend(table_tag.tables)
            for enum_tag in self.soupy_enumeration_tags:
                self.tables.extend(enum_tag.tables)

    def parse(self):
        self.soupy_table_tags = []
        for i, t in enumerate(self.soup.find_all('table')):
            print(f"Parsing table block {i+1}...")
            self.soupy_table_tags.append(HtmlTableTagParser(t, auto_parse=self.auto_parse))
            print(f"Parsing table block {i+1} complete")

        self.soupy_enumeration_tags = []
        for i, ol in enumerate(self.soup.find_all('ol')):
            print(f"Parsing enumeration block {i+1}...")
            self.soupy_enumeration_tags.append(HtmlTableEnumerationParser(ol, auto_parse=self.auto_parse))
            print(f"Parsing enumeration block {i+1} complete")


class SubmissionParser(HtmlParser):
    def __init__(self, submission: Submission, auto_parse=False):
        html = submission.selftext_html
        super(SubmissionParser, self).__init__(html, auto_parse)


class CommentParser(HtmlParser):
    def __init__(self, comment: Comment, auto_parse=False):
        html = comment.body_html
        super(CommentParser, self).__init__(html, auto_parse)


def get_links_from_text(html_text, restrict_by_domain="reddit.com"):
    soup = BeautifulSoup(html_text, HTML_PARSER)
    all_links = soup.findAll('a')
    return [(link.text, link['href'])
            for link in all_links
            if restrict_by_domain is None
            or restrict_by_domain in link['href']]


def string_is_die_roll(s):
    try:
        dice.parse_expression(s)
        return True
    except (ParseException, ParseFatalException) as e:
        print(f"Got exception {e} when rolling {s}.  Assuming it is not a valid roll string.")
        return False


# TODO: Known issue: d00 should be recognized and converted to d10?  d100?  Or left as inference?
