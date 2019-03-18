#!/usr/bin/env python3
"""These classes define the workload for a given request.
A single request will spawn a single Workload.
WorkItems will be processed and grow a WorkLog, which will be a tree consisting of each job executed,
   with possible children WorkLog items if a given WorkItem requires additional worknodes.
E.g., the following will all be represented by a single WorkItem, each spawning the next in the tree.
* Initial request parsing
* Parsing of a particular text for table (such as the OP or comment itself)
* Identifying that rolls are needed for a table, such as a "wide table"
* Performing and saving the outcome of the roll of a given table within the wide table.

Because the WorkLog is a tree in structure, the final response can be aggregated by parents, e.g.,
the response will consist of paragraph-separated sections for each parsed zone,
each parsed zone will consist of the outcome for each table,
a particular wide-table might be formatted different, aggregating its children's results.

Work is not necessarily processed in order, since modularity is ideal and any information required by one WorkItem
should be specified by its parent.
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, Any

import dice
from anytree import RenderTree

import rofm.classes.core.worknodes.rofm_requests
# noinspection PyMethodParameters
from rofm.classes.core.worknodes.rofm_core import Worknode, WorkloadType
from rofm.classes.reddit import Reddit, comment_contains_username
from rofm.classes.tables import Table

logging.getLogger().setLevel(logging.DEBUG)


@dataclass
class RollTable(Worknode):
    args: Table
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.roll_table
    name: str = "Roll table"

    def __str__(self):
        # A rolled table should have one child holding the value.
        rolled_value = self.children[0].output
        return f"{self.args.description}:    \n{self.args.dice} -> {rolled_value}: {self.args.get(rolled_value)}\n\n\n"

    def __repr__(self):
        return super(RollTable, self).__repr__()

    def _my_work_resolver(self):
        self.additional_work.append(RollAny(self.args.dice))


@dataclass
class RollAny(Worknode):
    args: str  # Dice string
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.roll_for_table_outcome
    name: str = "Roll the dice"

    def __str__(self):
        raise NotImplementedError("RollAny not expected to be posted directly.  Fetch value from output.")

    def __repr__(self):
        return super(RollAny, self).__repr__()

    def _my_work_resolver(self):
        return dice.roll(self.args)


if __name__ == '__main__':
    def do_test_run_with_pm():
        import rofm.classes.core.worknodes.rofm_requests
        Reddit.login()

        pm = next(Reddit.r.inbox.messages())
        node = rofm.classes.core.worknodes.rofm_requests.PrivateMessage(pm)
        node.do_all_work()
        node_render = RenderTree(node)
        shifted_node_render = " " * 4 + "\n    ".join(str(node_render).split("\n"))
        return shifted_node_render


    def do_test_run_with_mention():
        Reddit.login()

        random_mention = next(mention for mention in Reddit.r.inbox.all() if comment_contains_username(mention))
        node = rofm.classes.core.worknodes.rofm_requests.UsernameMention(random_mention)
        node.do_all_work()
        node_render = RenderTree(node)
        shifted_node_render = " " * 4 + "\n    ".join(str(node_render).split("\n"))
        return shifted_node_render


    print(do_test_run_with_mention())

#
# TODO: 'https://www.reddit.com/r/DnDBehindTheScreen/comments/ale18z/oneroll_society_blunderbuss_engine/'
# Sub-enumeration doesn't parse well, but that's maybe okay.  Perceived header as parent header.
# Also rolled the random enumeration for the mission-statement.  Maybe lock free-standing and others by a [[roll all]]

# TODO: Improve header detection for free-standing enumerations.

# TODO d100 subreddit
