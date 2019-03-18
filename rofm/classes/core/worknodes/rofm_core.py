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
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Tuple, Optional, List, Any

from anytree import NodeMixin, PreOrderIter

logging.getLogger().setLevel(logging.DEBUG)


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class WorkloadType(str, AutoName):
    """Every Workload / WorkNode should refer to a definitive type to determine behavior."""
    # Level "zero" request types
    request_type_username_mention = auto()
    request_type_private_message = auto()

    # Parsing actions
    parse_for_reddit_domain_urls = auto()
    parse_top_level_comments = auto()
    parse_for_special_requests = auto()
    parse_item_for_tables = auto()

    # Rolling actions
    roll_table = auto()
    roll_for_table_outcome = auto()
    roll_stats = auto()
    roll_specific_request = auto()

    # Other actions
    follow_link = auto()


@dataclass
class Worknode(ABC, NodeMixin):
    args: Tuple[Any]
    kwargs: Dict[str, Any]

    # This is for node-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict, init=False)

    # These are overwritten by child classes
    workload_type: WorkloadType = field(default=None, init=False, repr=False)
    name: str = field(default=None, init=False, repr=False)

    # These are updated when worknodes is done
    work_done: bool = field(default=None, init=False)
    output: Optional[Any] = field(default=None, init=False)
    exception: Optional[Exception] = field(default=None, init=False)
    additional_work: List["Worknode"] = field(default_factory=list, init=False)

    def __init__(self, *args, **kwargs):
        super(Worknode, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def do_all_work(self):
        for node in PreOrderIter(self):
            node.do_my_work()

    def do_my_work(self):
        try:
            self.output = self._my_work_resolver()
        except Exception as e:
            self.exception = e

        for child in self.additional_work:
            child.parent = self

        self.work_done = True

    @abstractmethod
    def _my_work_resolver(self):
        pass

    @abstractmethod
    def __str__(self):
        """Gets Reddit response string."""
        return repr(self)

    def __repr__(self):
        display_name = self.name or self.__class__.__name__

        in_as_string = '('
        in_as_string += f"{self.args}" if self.args else ''
        in_as_string += ',' if self.args and self.kwargs else ''
        in_as_string += f"{self.kwargs}" if self.kwargs else ''
        in_as_string += ')'

        out_as_string = (
            f"-> !! threw {self.exception}" if self.exception else
            f"-> {self.output}" if self.output else "")

        return f"<{display_name} :: {in_as_string} {out_as_string}>"


# if __name__ == '__main__':
    # from rofm.classes.core.worknodes.requests import PrivateMessage
    #
    # Reddit.login()
    # pm = next(Reddit.r.inbox.messages())
    # pm_node = PrivateMessage(pm)
    # pm_node.name = "test pm"
    # pm_node.do_all_work()
    #
    # node_render = RenderTree(pm_node)
    # shifted_node_render = " " * 4 + "\n    ".join(str(node_render).split("\n"))
    # print(shifted_node_render)
