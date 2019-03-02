#!/usr/bin/env python3

from rofm.classes.reddit import Reddit

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
    pm = next(Reddit.r.inbox.messages())
    # node = WorkNode(WorkloadType.request_type_private_message, pm, name="test pm")
    # node.do_all_work()
    # node_render = RenderTree(node)
    # shifted_node_render = " " * 4 + "\n    ".join(str(node_render).split("\n"))
    # print(shifted_node_render)
    #
    # random_mention = next(mention for mention in Reddit.r.inbox.all() if comment_contains_username(mention))
    # work = WorkNode(WorkloadType.request_type_username_mention, random_mention)
    # work.do_all_work()
    # render = RenderTree(work)
    # shifted_render = " " * 4 + "\n    ".join(str(render).split("\n"))
    # print(shifted_render)
#
# TODO: 'https://www.reddit.com/r/DnDBehindTheScreen/comments/ale18z/oneroll_society_blunderbuss_engine/'
# Sub-enumeration doesn't parse well, but that's maybe okay.  Perceived header as parent header.
# Also rolled the random enumeration for the mission-statement.  Maybe lock free-standing and others by a [[roll all]]

# TODO: Improve header detection for free-standing enumerations.

# TODO d100 subreddit
