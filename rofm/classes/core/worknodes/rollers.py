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

# noinspection PyMethodParameters
from rofm.classes.core.worknodes.core import Worknode, WorkloadType
from rofm.classes.core.worknodes.requests import PrivateMessage
from rofm.classes.reddit import Reddit
from rofm.classes.tables import Table

logging.getLogger().setLevel(logging.DEBUG)


@dataclass
class RollTable(Worknode):
    args: Table
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.roll_table
    name: str = "Roll table"

    def __str__(self):
        raise NotImplementedError("Special requests not yet implemented.")

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
        raise NotImplementedError("Special requests not yet implemented.")

    def __repr__(self):
        return super(RollAny, self).__repr__()

    def _my_work_resolver(self):
        return dice.roll(self.args)


if __name__ == '__main__':
    Reddit.login()
    pm = next(Reddit.r.inbox.messages())
    pm_node = PrivateMessage(pm)
    pm_node.name = "test pm"
    pm_node.do_all_work()

    node_render = RenderTree(pm_node)
    shifted_node_render = " " * 4 + "\n    ".join(str(node_render).split("\n"))
    print(shifted_node_render)
