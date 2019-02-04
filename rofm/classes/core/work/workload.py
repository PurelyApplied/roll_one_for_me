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
import logging
from dataclasses import dataclass, field
from enum import Enum

from anytree import LevelOrderIter, RenderTree, NodeMixin, PreOrderIter
from typing import Dict, Tuple, Optional


class WorkloadType(str, Enum):
    """Every Workload / WorkloadNode should refer to a definitive type to determine behavior."""
    # Level "zero" request types
    username_mention = "username_mention"
    private_message = "private_message"
    chat = "chat"

    # Top-level types
    respond_with_private_message_apology = "apologize"
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
    args: Optional[Tuple] = ()
    kwargs: Optional[Dict] = field(default_factory=dict)
    finished: bool = False
    output = None


class WorkloadNode(Workload, NodeMixin):
    """anytree Workload hybrid.  Used to traverse the work tree, generating child nodes as needed."""

    work_resolution = {}   # This is populated via the @workload_resolver decorator.
    logger = logging.getLogger(f"{__name__}::WorkloadNode")
    logger.setLevel(logging.DEBUG)

    def __init__(self, work_type: WorkloadType, args=(), *, name=None, parent=None):
        super(WorkloadNode, self).__init__(work_type, args)
        self.parent = parent
        self.name = name if name else f"'{work_type.name}'"

    def do_all_work(self):
        for node in PreOrderIter(self):
            node.do_my_work()

    def do_my_work(self):
        """Examine the type of work you are and delegate it out."""
        self.logger.info(f"Node {self} is doing work...")

        resolver = self.work_resolution[self.work_type]
        print(f"Resolving work of {self} via: {resolver}(*{self.args}, **{self.kwargs}")
        new_work = resolver(*self.args, **self.kwargs)

        if new_work:
            for child in new_work:
                child.parent = self
        self.finished = True

    def __repr__(self):
        return f"<WorkNode {self.name}>"

    def work(self):
        for node in LevelOrderIter(self):
            node.__do_work()

    @classmethod
    def _register_resolver(cls, work_type, registered_resolver, override=False):
        """Registers a workload resolver.  Please decorate your functions with @.workload_resolver instead."""
        assert override or work_type not in cls.work_resolution, f"Resolver for {work_type} already present."
        cls.work_resolution[work_type] = registered_resolver

    @classmethod
    def workload_resolver(cls, *work_types, override=False):
        """Registers the decorated function as the resolver for the given work_type.
        If additional work is required, the decorated function should return a collection containing the
        additional WorkloadNode containers.  Parent-child relationship will be written after return."""

        assert work_types, "Specify at least one WorkloadType to resolve via this function."

        def decorator(f):
            for wt in work_types:
                cls._register_resolver(wt, f, override=override)
            return f
        return decorator


@WorkloadNode.workload_resolver(*WorkloadType)
def not_yet_implemented():
    pass


@WorkloadNode.workload_resolver(WorkloadType.username_mention, override=True)
def resolve_username_mention():
    return WorkloadNode(WorkloadType.default_request),


@WorkloadNode.workload_resolver(WorkloadType.default_request, override=True)
def resolve_default_request():
    return (WorkloadNode(WorkloadType.parse_op),
            WorkloadNode(WorkloadType.parse_comment_for_table),
            WorkloadNode(WorkloadType.parse_top_level_comments))


@WorkloadNode.workload_resolver(WorkloadType.parse_op, override=True)
def resolve_parse_op():
    return (WorkloadNode(WorkloadType.roll_table, name="Roll table 1", args=("Table 1",)),
            WorkloadNode(WorkloadType.roll_table, name="Roll table 2", args=("Table 2",)),
            WorkloadNode(WorkloadType.roll_table, name="Roll table 3", args=("Table 3",)),
            WorkloadNode(WorkloadType.roll_table, name="Roll table 4", args=("Table 4",)),)


@WorkloadNode.workload_resolver(WorkloadType.parse_comment_for_table, override=True)
def resolve_parse_comment_for_table():
    return WorkloadNode(WorkloadType.roll_table, args=("Table from comment",)),


@WorkloadNode.workload_resolver(WorkloadType.parse_top_level_comments, override=True)
def resolve_parse_top_level_comments():
    return tuple(WorkloadNode(WorkloadType.parse_comment_for_table) for _ in range(3))


@WorkloadNode.workload_resolver(WorkloadType.roll_table, override=True)
def resolve_parse_top_level_comments(table_name):
    print(f"I'm rolling table {table_name}")


if __name__ == '__main__':
    root = WorkloadNode(work_type=WorkloadType.default_request, name="Initial request")
    root.do_all_work()
    print(RenderTree(root))
