#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import List, Tuple

import dice
from bs4 import BeautifulSoup, Tag
from pyparsing import ParseBaseException

from rofm.classes.reddit import Reddit, comment_contains_username
from rofm.classes.tables import Table, SimpleTable

HTML_PARSER = 'html.parser'


@dataclass
class TableContainer:
    tables: List[Table] = field(default_factory=list)


class HtmlTableEnumerationParser(TableContainer):
    """Necessarily a single table."""
    soupy_enumerations: Tag
    auto_parse = False

    soupy_items: List[str] = None
    table: Table = None

    def __init__(self, soupy_enumeations: Tag, auto_parse=False):
        possibly_a_header = soupy_enumeations.find_previous_sibling('p')
        self.soupy_items = soupy_enumeations.find_all('li')

        dice_roll, desc = self._get_roll_and_dec(possibly_a_header)

        table = SimpleTable(dice_roll, [item.text for item in self.soupy_items], description=desc)
        self.tables = [table]
        print(self)

    def _get_roll_and_dec(self, possibly_a_header):
        """If the header starts with a die roll, returns that die roll and the remaining line.
        Otherwise, returns the presumed die roll (1d<item count>) and a hopeful description."""
        stripped = list(possibly_a_header.stripped_strings)
        try:
            dice.parse_expression(stripped[0])
            return stripped[0], " ".join(stripped[1:])
        except ParseBaseException as e:
            print(f"Got exception {e} when rolling {stripped[0]}.  Probably not a die.")
            return "A free-standing enumeration", f"d{len(self.soupy_items)}"


class HtmlTableTagParser(TableContainer):
    """Possibly a wide table / multiple tables."""
    soupy_table: Tag
    auto_parse = False

    soupy_items: List[str] = None
    table: Table = None

    def __init__(self, soupy_table: Tag, auto_parse=False):
        self.soupy_table = soupy_table
        self.auto_parse = auto_parse

        if auto_parse:
            self.parse()

    def parse(self):
        self.soupy_items = self.soupy_table.find_all('tr')

        print(self)


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

    def parse(self):
        self.soupy_table_tags = [HtmlTableTagParser(t, auto_parse=self.auto_parse) for t in self.soup.find_all('table')]
        self.soupy_enumeration_tags = [HtmlTableEnumerationParser(ol, auto_parse=self.auto_parse) for ol in self.soup.find_all('ol')]


headered_enumeration_submission_example = \
    r'https://www.reddit.com/r/DnDBehindTheScreen/comments/ain51n/party_bond_generator_tables/'
headered_enumeration_submission_example2 = \
    r'https://www.reddit.com/r/DnDBehindTheScreen/comments/ale18z/oneroll_society_blunderbuss_engine/'
unheadered_enumeration_submisison_example = \
    r'https://www.reddit.com/r/DnDBehindTheScreen/comments/agp2ik/the_scene_of_the_crime_a_generator/'
two_col_table_submission_example = \
    r'https://www.reddit.com/r/DnDBehindTheScreen/comments/8zuqit/charts_for_quickly_rolling_up_a_short_adventure/'
two_col_weighted_outcome_submission_example = \
    r'https://www.reddit.com/r/DnDBehindTheScreen/comments/8grlha/table_of_5e_rings/'
wide_table_submission_example = \
    r'https://www.reddit.com/r/BehindTheTables/comments/ahba3r/trail_rations/'

if __name__ == '__main__':
    Reddit.login()
    things = [Reddit.r.submission(url=x) for x in (headered_enumeration_submission_example,
                                                   headered_enumeration_submission_example2,
                                                   unheadered_enumeration_submisison_example,
                                                   two_col_table_submission_example,
                                                   two_col_weighted_outcome_submission_example,
                                                   wide_table_submission_example,
                                                   )]
    parsers = [HtmlParser(s.selftext_html, auto_parse=True) for s in things]
    random_mention = next(mention for mention in Reddit.r.inbox.all() if comment_contains_username(mention))
    # work = WorkNode(WorkloadType.username_mention, args=(random_mention,))
    # work.do_all_work()
    # print(RenderTree(work))

    soup = BeautifulSoup(random_mention.submission.selftext_html, 'html.parser')
    parser = HtmlParser(random_mention.submission.selftext_html, auto_parse=True)

