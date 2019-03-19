#!/usr/bin/env python3
import logging

from anytree import RenderTree

import rofm.classes.worknodes
# noinspection PyMethodParameters
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

logging.getLogger().setLevel(logging.DEBUG)


def do_test_run_with_pm():
    Reddit.login()

    pm = next(Reddit.r.inbox.messages())
    node = rofm.classes.worknodes.PrivateMessage(pm)
    node.do_all_work()
    node_render = RenderTree(node)
    shifted_node_render = " " * 4 + "\n    ".join(str(node_render).split("\n"))
    return node, shifted_node_render


def do_test_run_with_mention():
    Reddit.login()

    mentions = (mention for mention in Reddit.r.inbox.all() if comment_contains_username(mention))
    _, random_mention = next(mentions), next(mentions)
    node = rofm.classes.worknodes.UsernameMention(random_mention)
    node.do_all_work()
    node_render = RenderTree(node)
    shifted_node_render = " " * 4 + "\n    ".join(str(node_render).split("\n"))
    return node, shifted_node_render


if __name__ == '__main__':
    _node, render = do_test_run_with_mention()
    print(render)
    print(str(_node))
