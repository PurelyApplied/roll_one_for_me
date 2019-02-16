#!/usr/bin/env python3
from anytree import RenderTree

from rofm.classes.core.work.workload import WorkNode, WorkloadType
from rofm.classes.reddit import Reddit, comment_contains_username

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
    # some_links = (headered_enumeration_submission_example,
    #               headered_enumeration_submission_example2,
    #               unheadered_enumeration_submisison_example,
    #               two_col_table_submission_example,
    #               two_col_weighted_outcome_submission_example,
    #               wide_table_submission_example,)
    # things = [Reddit.r.submission(url=x) for x in some_links]
    # parsers = []
    # for i, s in enumerate(things):
    #     print(f"Table {i+1}...")
    #     parsers.append(HtmlParser(s.selftext_html, auto_parse=True))
    #     print(f"Table {i + 1} done")
    #     print()
    # look_here = [{'link': l, 'parser': p} for p, l in zip(parsers, some_links)]
    # pass
    Reddit.r.inbox.messages()
    random_mention = next(mention for mention in Reddit.r.inbox.all() if comment_contains_username(mention))
    work = WorkNode(WorkloadType.username_mention, args=(random_mention,))
    work.do_all_work()
    print(RenderTree(work))

    # soup = BeautifulSoup(random_mention.submission.selftext_html, 'html.parser')
    # parser = HtmlParser(random_mention.submission.selftext_html, auto_parse=True)

# TODO: 'https://www.reddit.com/r/DnDBehindTheScreen/comments/ale18z/oneroll_society_blunderbuss_engine/'
# Sub-enumeration doesn't parse well, but that's maybe okay.  Perceived header as parent header.
# Also rolled the random enumeration for the mission-statement.  Maybe lock free-standing and others by a [[roll all]]

# TODO: Improve header detection for free-standing enumerations.
