#!/usr/bin/env python3

from typing import List, Tuple

from anytree import RenderTree
from bs4 import BeautifulSoup, Tag

from rofm.classes.core.work.workload import WorkNode, WorkloadType
from rofm.classes.reddit import Reddit, comment_contains_username
from rofm.classes.tables.table import Table

HTML_PARSER = 'html.parser'


class HtmlTable:
    soupy_table: Tag
    auto_parse = False

    soupy_items: List[str] = None
    table: Table = None
    soup: BeautifulSoup = None

    def __init__(self, soupy_table: Tag, auto_parse=False):
        self.soupy_table = soupy_table
        self.auto_parse = auto_parse

        if auto_parse:
            self.parse()

    def parse(self):
        self.soupy_items = self.soupy_table.find_all('tr')


class HtmlParser:
    html_text: str
    auto_parse = False
    soupy_table_tags: List[HtmlTable] = None
    soupy_enumeration_with_header_pairs: List[Tuple[Tag, Tag]] = None

    soup: BeautifulSoup = None

    def __init__(self, html_text: str, auto_parse=False):
        self.html_text = html_text
        self.auto_parse = auto_parse
        self.soup = BeautifulSoup(self.html_text, HTML_PARSER)

        if auto_parse:
            self.parse()

    def parse(self):
        self.soupy_table_tags = [HtmlTable(t, auto_parse=self.auto_parse) for t in self.soup.find_all('table')]

        tag_set = self.soup.find_all(name=('ol', 'p'))
        # This should be impossible, but when did a sanity check ever hurt?
        if len(tag_set) == 0:
            self.soupy_enumeration_with_header_pairs = []
            return

        before, after = iter(tag_set), iter(tag_set)
        next(after)
        self.soupy_enumeration_with_header_pairs = [(b if b.name == 'p' else None, a) for b, a in zip(before, after) if a.name == 'ol']


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
    work = WorkNode(WorkloadType.username_mention, args=(random_mention,))
    work.do_all_work()
    print(RenderTree(work))

    soup = BeautifulSoup(random_mention.submission.selftext_html, 'html.parser')
    parser = HtmlParser(random_mention.submission.selftext_html, auto_parse=True)

