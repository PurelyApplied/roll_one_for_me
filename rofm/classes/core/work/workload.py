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
from enum import Enum, auto
from functools import wraps
from typing import Dict, Tuple, Optional, List, Callable, Any

from anytree import NodeMixin, PreOrderIter
from praw.models import Comment, Submission, Message

# noinspection PyMethodParameters
from rofm.classes.html_parsers import CommentParser, SubmissionParser
from rofm.classes.tables import Table
from rofm.classes.util.decorators import with_class_logger
from rofm.classes.util.misc import split_iterable, get_text_from_comment_submission_or_message

logging.getLogger().setLevel(logging.DEBUG)


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class WorkloadType(str, AutoName):
    """Every Workload / WorkNode should refer to a definitive type to determine behavior."""
    # Level "zero" request types
    username_mention = auto()
    private_message = auto()
    chat = auto()

    # Parsing actions
    parse_op = auto()
    parse_for_reddit_domain_urls = auto()
    parse_top_level_comments = auto()
    parse_comment_for_table = auto()
    parse_arbitrary_text_for_table = auto()
    parse_table = auto()
    parse_wide_table = auto()
    perform_basic_roll = auto()
    perform_compound_roll = auto()

    # Rolling actions
    roll_stats = auto()
    roll_specific_request = auto()
    roll_table = auto()
    roll_this_die = auto()

    # Other actions
    respond_with_private_message_apology = auto()
    default_request = auto()
    follow_link = auto()


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


@with_class_logger
class WorkNode(Workload, NodeMixin):
    def __init__(self, work_type: WorkloadType, args=(), *, name=None, parent=None):
        super(WorkNode, self).__init__(work_type, args)
        self.parent = parent
        self.name = name if name else f"'{work_type.name}'"

    def __repr__(self):
        rep = f"{self.name}"
        rep += f" :: output = {self.output}" if self.output else ""
        return f"<WorkNode {rep}>"

    def do_all_work(self):
        for node in PreOrderIter(self):
            node.do_my_work()

    def do_my_work(self):
        """Examine the type of work you are and delegate it out."""
        self.logger.info(f"Node {self} is doing work...")

        resolver = WorkResolver.get(self.work_type)
        self.logger.debug(f"Resolving work of {self} via: {resolver.__name__}(*{self.args}, **{self.kwargs}")
        new_work, self.output = resolver(*self.args, **self.kwargs)

        if new_work:
            for child in new_work:
                child.parent = self
        self.finished = True


@with_class_logger
class WorkResolverContainer:
    # These are registered via the decorator below.
    work_resolution: Dict[WorkloadType, Callable[[Any], Optional[typing.Iterable['WorkNode']]]] = {}

    @classmethod
    def _register_resolver(cls, work_type, registered_resolver, override=False):
        """Registers a workload resolver.  Please decorate your functions with @.workload_resolver instead."""
        assert override or work_type not in cls.work_resolution, f"Resolver for {work_type} already present."
        cls.logger.info(f"Registering resolver {work_type} -> {registered_resolver.__name__}")
        cls.work_resolution[work_type] = registered_resolver

    @classmethod
    def get(cls, item, default=None):
        return cls.work_resolution.get(item, default)

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
                try:
                    base_function_return_value = f(*args, **kwargs)
                except TypeError as e:
                    raise TypeError(f"TypeError in function {f.__name__}.  Probably incorrect arguments passed.") from e
                except Exception as e:
                    # For stability, log the exception but don't throw it back up.
                    base_function_return_value = e

                # Zero return arguments:
                if base_function_return_value is None:
                    return [], None

                # One return argument -- A single WorkNode is new work, else it's no new work and a return value
                if not isinstance(base_function_return_value, collections.Iterable):
                    if isinstance(base_function_return_value, WorkNode):
                        return [base_function_return_value], None
                    else:
                        return [], base_function_return_value
                # One return argument, iterable because it's a string.
                elif isinstance(base_function_return_value, str):
                    return [], base_function_return_value

                # Separate out the WorkNode types to become children.
                workload, outputs = split_iterable(base_function_return_value,
                                                   lambda item: isinstance(item, WorkNode))
                return workload, outputs

            for wt in work_types:
                cls._register_resolver(wt, decorated_function, override=override)
            return decorated_function

        return decorator


@with_class_logger
class WorkResolver(WorkResolverContainer):
    """This class handles simple work generation and delegation.
    For instance, the resolver for WorkType.parse_top_level_comments identifies the top level comments, and
    returns the WorkNode for parsing each individual comment, to be handled downstream.
    """

    @staticmethod
    @WorkResolverContainer.workload_resolver(WorkloadType.parse_top_level_comments)
    def scan_top_level_comments(comments: List[Comment]):
        return [WorkNode(WorkloadType.parse_comment_for_table, args=(comment,), name=f"Top-level comment {i + 1}")
                for i, comment in enumerate(comments)]

    @staticmethod
    @WorkResolverContainer.workload_resolver(WorkloadType.parse_comment_for_table)
    def parse_comment_for_table(comment: Comment):
        comment_parser = CommentParser(comment, auto_parse=True)
        return [WorkNode(WorkloadType.roll_table, (t,)) for t in comment_parser.tables] or "No table found in comment"

    @staticmethod
    @WorkResolverContainer.workload_resolver(WorkloadType.roll_table)
    def roll_table(table: Table):
        return table.roll()

    @staticmethod
    @WorkResolverContainer.workload_resolver(WorkloadType.parse_op)
    def parse_comment_for_table(submission: Submission):
        submission_parser = SubmissionParser(submission, auto_parse=True)
        return [WorkNode(WorkloadType.roll_table, (t,)) for t in submission_parser.tables] or "No table found in submission"

    @staticmethod
    @WorkResolverContainer.workload_resolver(WorkloadType.private_message)
    def process_private_message(mention: Comment):

        raise NotImplementedError(f"{__name__} not implemented")

    @staticmethod
    @WorkResolverContainer.workload_resolver(WorkloadType.parse_for_reddit_domain_urls)
    def scan_for_reddit_links(obj: typing.Union[Comment, Submission, Message]):
        html_text = get_text_from_comment_submission_or_message(obj)
        raise NotImplementedError(f"{__name__} not implemented")

    @staticmethod
    @WorkResolverContainer.workload_resolver(WorkloadType.username_mention)
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
        if mention in top_level_comments:
            top_level_comments.remove(mention)
        return (WorkNode(WorkloadType.parse_comment_for_table, args=(mention,), name="Look in mention for tables"),
                WorkNode(WorkloadType.parse_for_reddit_domain_urls, args=(mention,), name="Search for Reddit links"),
                WorkNode(WorkloadType.parse_op, args=(op,), name="Search OP for tables"),
                WorkNode(WorkloadType.parse_top_level_comments, args=(top_level_comments,),
                         name=f"Search {len(top_level_comments)} different top-level comments for tables."),)


if __name__ == '__main__':
    resolved, unresolved = split_iterable(WorkloadType, lambda x: WorkResolver.get(x, None) is not None)
    for _type in resolved:
        _resolver = WorkResolver.get(_type, None)
        print(f"Type WorkResolver.{_type} resolved by {_resolver.__name__}")

    print()
    for _type in unresolved:
        print(f"No resolver yet for WorkResolver.{_type}")

