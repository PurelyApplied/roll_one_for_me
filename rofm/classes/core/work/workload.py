#!/usr/bin/env python3
"""These classes define the workload for a given request.
A single request will spawn a single Workload.
WorkItems will be processed and grow a WorkLog, which will be a tree consisting of each job executed,
   with possible children WorkLog items if a given WorkItem requires additional work.
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
from dataclasses import dataclass
from enum import Enum

from anytree import LevelOrderIter, RenderTree, NodeMixin, PreOrderIter


class WorkloadType(str, Enum):
    """Every Workload / WorkloadNode should refer to a definitive type to determine behavior."""
    # Level "zero" request types
    username_mention = "username_mention"
    private_message = "private_message"
    chat = "chat"

    # Top-level types
    default_request = "default_request"
    parse_op = "parse_op"
    parse_top_level_comments = "parse_top_level_comments"
    parse_comment_for_table = "parse_comment_for_table"
    follow_link = "follow_link"

    roll_stats = "roll_stats"
    roll_specific_request = "roll_specific_request"
    roll_table = "roll_table"

    # Intermediate and subordinate types
    parse_table = "parse_table"
    parse_wide_table = "parse_wide_table"
    perform_basic_roll = "perform_basic_roll"
    perform_compound_roll = "perform_compound_roll"


@dataclass
class Workload:
    """Container class for workload type, arguments, and output."""
    work_type: WorkloadType
    args: ()
    finished: bool = False
    output = None


class WorkloadNode(Workload, NodeMixin):
    """anytree Workload hybrid.  Used to traverse the work tree, generating child nodes as needed."""

    def __init__(self, work_type: WorkloadType, args=(), *, name=None, parent=None):
        super(WorkloadNode, self).__init__(work_type, args)
        self.parent = parent
        self.name = name if name else f"'{work_type.name}'"

    def do_all_work(self):
        for node in PreOrderIter(self):
            node.do_my_work()

    def do_my_work(self):
        print(f"Node {self} is doing work...")
        if self.work_type == WorkloadType.username_mention:
            WorkloadNode(WorkloadType.default_request, parent=self)
        if self.work_type == WorkloadType.default_request:
            WorkloadNode(WorkloadType.parse_op, parent=self)
            WorkloadNode(WorkloadType.parse_comment_for_table, parent=self)
            WorkloadNode(WorkloadType.parse_top_level_comments, parent=self)
        if self.work_type == WorkloadType.parse_op:
            WorkloadNode(WorkloadType.roll_table, args=("Table 1",), parent=self)
            WorkloadNode(WorkloadType.roll_table, args=("Table 2",), parent=self)
            WorkloadNode(WorkloadType.roll_table, args=("Table 3",), parent=self)
            WorkloadNode(WorkloadType.roll_table, args=("Table 4",), parent=self)
        if self.work_type == WorkloadType.parse_comment_for_table:
            WorkloadNode(WorkloadType.roll_table, args=("Table from comment",), parent=self)
        if self.work_type == WorkloadType.parse_top_level_comments:
            for _ in range(3):
                WorkloadNode(WorkloadType.parse_comment_for_table, parent=self)

        self.finished = True

    def __repr__(self):
        return f"<WorkNode {self.name}>"

    def work(self):
        for node in LevelOrderIter(self):
            node.__do_work()


if __name__ == '__main__':
    # root = WorkloadNode("root")
    # root.work()
    # print(RenderTree(root))

    root = WorkloadNode(work_type=WorkloadType.default_request, name="Initial request")
    root.do_all_work()
    print(RenderTree(root))
