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
import collections
import logging
import typing
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from random import randint
from typing import Dict, Tuple, Optional, List, Callable, Any

from anytree import LevelOrderIter, NodeMixin, PreOrderIter
from praw.models import Comment, Submission

from rofm.legacy.models import TableSourceFromText, Table


class WorkloadType(str, Enum):
    """Every Workload / WorkNode should refer to a definitive type to determine behavior."""
    # Level "zero" request types
    username_mention = "username_mention"
    private_message = "private_message"
    chat = "chat"

    # Parsing actions
    parse_op = "parse_op"
    parse_for_reddit_domain_urls = "parse_for_reddit_domain_urls"
    parse_top_level_comments = "parse_top_level_comments"
    parse_comment_for_table = "parse_comment_for_table"
    parse_arbitrary_text_for_table = "parse_arbitrary_text_for_table"
    parse_table = "parse_table"
    parse_wide_table = "parse_wide_table"
    perform_basic_roll = "perform_basic_roll"
    perform_compound_roll = "perform_compound_roll"

    # Rolling actions
    roll_stats = "roll_stats"
    roll_specific_request = "roll_specific_request"
    roll_table = "roll_table"
    roll_this_die = "roll_this_die"

    # Other actions
    respond_with_private_message_apology = "apologize"
    default_request = "default_request"
    follow_link = "follow_link"


class WorkloadOutput:
    """This class exists only for the convenience of typing, since some types are ignored in Union[]"""


@dataclass
class Workload:
    """Container class for workload type, arguments, and output."""
    work_type: WorkloadType
    args: Optional[Tuple] = ()
    kwargs: Optional[Dict] = field(default_factory=dict)
    finished: bool = False
    output = None


def split_iterable(iterable, split_condition):
    list_satisfying = []
    list_not_satisfying = []
    for item in iterable:
        if split_condition(item):
            list_satisfying.append(item)
        else:
            list_not_satisfying.append(item)
    return list_satisfying, list_not_satisfying


class WorkNode(Workload, NodeMixin):
    """The WorkNode is the fundamental unit for our workload graph.
    Each WorkNode corresponds to one WorkloadType, executing the function associated to that type with the
    @WorkNode.workload_resolver decorator.  See the decorator's docstring for more information.
    """

    # This is populated via the @workload_resolver decorator.
    work_resolution: Dict[WorkloadType, Callable[[Any], Optional[typing.Iterable['WorkNode']]]] = {}
    logger = logging.getLogger(f"{__name__}::WorkNode")

    def __init__(self, work_type: WorkloadType, args=(), *, name=None, parent=None):
        super(WorkNode, self).__init__(work_type, args)
        self.parent = parent
        self.name = name if name else f"'{work_type.name}'"

    def do_all_work(self):
        for node in PreOrderIter(self):
            node.do_my_work()

    def do_my_work(self):
        """Examine the type of work you are and delegate it out."""
        self.logger.info(f"Node {self} is doing work...")

        resolver = self.work_resolution[self.work_type]
        self.logger.debug(f"Resolving work of {self} via: {resolver.__name__}(*{self.args}, **{self.kwargs}")
        new_work, self.output = resolver(*self.args, **self.kwargs)

        if new_work:
            for child in new_work:
                child.parent = self
        self.finished = True

    def __repr__(self):
        rep = f"{self.name}"
        rep += f" :: output = {self.output}" if self.output else ""
        return f"<WorkNode {rep}>"

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

        The registered function
        If additional work is required, the decorated function should return a collection containing the
        additional WorkNode containers.  Parent-child relationship will be written after return."""

        assert work_types, "Specify at least one WorkloadType to resolve via this function."

        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs) -> Tuple[typing.Iterable[WorkNode],
                                                             Optional[typing.Iterable[WorkloadOutput]]]:
                base_function_return_value = f(*args, **kwargs)
                # Zero return arguments:
                if base_function_return_value is None:
                    return [], None

                # One return argument:
                if not isinstance(base_function_return_value, collections.Iterable):
                    if isinstance(base_function_return_value, WorkNode):
                        return [base_function_return_value], None
                    else:
                        return [], base_function_return_value

                # Separate out the WorkNode types to become children.
                workload, outputs = split_iterable(base_function_return_value,
                                                   lambda item: isinstance(item, WorkNode))
                return workload, outputs

            for wt in work_types:
                cls._register_resolver(wt, decorated_function, override=override)
            return decorated_function

        return decorator


# noinspection PyUnusedLocal
@WorkNode.workload_resolver(*WorkloadType)
def not_yet_implemented(*args, **kwargs):
    raise NotImplementedError("Hey ya dingus.  You didn't implement that work type yet!")


@WorkNode.workload_resolver(WorkloadType.parse_top_level_comments, override=True)
def scan_top_level_comments(comments: List[Comment]):
    return [WorkNode(WorkloadType.parse_comment_for_table, args=(comment,), name=f"Top-level comment {i + 1}")
            for i, comment in enumerate(comments)]


@WorkNode.workload_resolver(WorkloadType.parse_comment_for_table, override=True)
def scan_comment_for_table(mention: Comment):
    return WorkNode(WorkloadType.parse_arbitrary_text_for_table, args=(mention.body,))


@WorkNode.workload_resolver(WorkloadType.roll_table, override=True)
def roll_a_table(table: Table):
    return randint(1, table.die)
    # return WorkNode(WorkloadType.roll_this_die, args=(table.die,), name=f"Roll d{table.die}")


@WorkNode.workload_resolver(WorkloadType.parse_arbitrary_text_for_table, override=True)
def scan_text_for_table(text: str):
    table_source = TableSourceFromText(text, "meaningless descriptor")
    if table_source.has_tables():
        return [WorkNode(WorkloadType.roll_table, args=(t,), name=f"Roll table {t.header}")
                for t in table_source.tables]


@WorkNode.workload_resolver(WorkloadType.parse_op, override=True)
def scan_submission_for_table(op: Submission):
    return WorkNode(WorkloadType.parse_arbitrary_text_for_table, args=(op.selftext,))


@WorkNode.workload_resolver(WorkloadType.username_mention, override=True)
def process_username_mention(mention: Comment):
    # Until it is decided otherwise, a mention gets three actions:
    # (1) Look at the comment itself for a table
    # (2) Look for reddit-domain links to parse.
    # (2.1) Distinguish from links to submission (which also get top-level comments) and
    # (2.2) Comments, which maybe get the full treatment?
    # (3) Look at the OP
    # (4) Look at the top-level comments.
    #
    op = mention.submission
    top_level_comments = list(op.comments)
    return (WorkNode(WorkloadType.parse_comment_for_table, args=(mention,), name="Look in mention for tables"),
            # WorkNode(WorkloadType.parse_for_reddit_domain_urls, args=(mention,), name="Search for Reddit links"),
            WorkNode(WorkloadType.parse_op, args=(op,), name="Search OP for tables"),
            WorkNode(WorkloadType.parse_top_level_comments, args=(top_level_comments,),
                     name="Search top-level comments for tables."),)
    pass


if __name__ == '__main__':
    for _type in WorkloadType:
        # noinspection PyTypeChecker
        if WorkNode.work_resolution.get(_type, not_yet_implemented) == not_yet_implemented:
            print(f"No resolver yet for {_type}")
