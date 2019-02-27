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
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Tuple, Optional, List, Any, Union

import dice
from anytree import NodeMixin, RenderTree, PreOrderIter
from praw.models import Comment, Submission, Message

# noinspection PyMethodParameters
from rofm.classes.core.work.workload import WorkloadType
from rofm.classes.html_parsers import CMSParser, get_links_from_text
from rofm.classes.reddit import Reddit
from rofm.classes.tables import Table
from rofm.classes.util.misc import get_html_from_cms

logging.getLogger().setLevel(logging.DEBUG)


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


@dataclass
class NewWorkload(ABC, NodeMixin):
    args: Tuple[Any]
    kwargs: Dict[str, Any]

    # This is for node-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict, init=False)

    # These are overwritten by child classes
    workload_type: WorkloadType = field(default=None, init=False, repr=False)
    name: str = field(default=None, init=False, repr=False)

    # These are updated when work is done
    work_done: bool = field(default=None, init=False)
    output: Optional[Any] = field(default=None, init=False)
    exception: Optional[Exception] = field(default=None, init=False)
    additional_work: List["NewWorkload"] = field(default_factory=list, init=False)

    def __init__(self, *args, **kwargs):
        super(NewWorkload, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def do_all_work(self):
        for node in PreOrderIter(self):
            node.work()

    def work(self):
        try:
            self.output = self.do_my_work()
        except Exception as e:
            self.exception = e

        for child in self.additional_work:
            child.parent = self

        self.work_done = True

    @abstractmethod
    def do_my_work(self):
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


@dataclass
class ParseTopLevelCommentsWorknode(NewWorkload):
    args: List[Comment]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_top_level_comments
    _name: str = "Top level comment parser"

    def do_my_work(self):
        for i, comment in enumerate(self.args):
            new_work = ParseCommentWorknode(comment)
            new_work.metadata = {'index': i, 'source': 'Comment'}
            self.additional_work.append(new_work)

    def __str__(self):
        return "asdasd" # super(ParseTopLevelCommentsWorknode, self).__str__()

    def __repr__(self):
        return super(ParseTopLevelCommentsWorknode, self).__repr__()


@dataclass
class ParseItemWorknode(NewWorkload):
    args: Union[Comment, Submission, Message]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_item_for_tables
    name: str = "Parse item of unidentified type"

    def __str__(self):
        return "asdasd" # super(ParseItemWorknode, self).__str__()

    def __repr__(self):
        return super(ParseItemWorknode, self).__repr__()

    def do_my_work(self):
        parsed_tables = CMSParser(self.args, auto_parse=True).tables
        if not parsed_tables:
            return "No tables found"

        for table in parsed_tables:
            self.additional_work.append(RollTableWorknode(table))


@dataclass
class ParseCommentWorknode(ParseItemWorknode):
    args: Comment
    name: str = "Comment parser"

    def __repr__(self):
        return super(ParseCommentWorknode, self).__repr__()


@dataclass
class ParseSubmissionWorknode(ParseItemWorknode):
    args: Submission
    name: str = "Submission parser"

    def __repr__(self):
        return super(ParseSubmissionWorknode, self).__repr__()


@dataclass
class ParseMessageWorknode(ParseItemWorknode):
    args: Message
    name: str = "Private message parser"

    def __repr__(self):
        return super(ParseMessageWorknode, self).__repr__()


@dataclass
class RollTableWorknode(NewWorkload):
    args: Table
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.roll_table
    name: str = "Roll table"

    def __str__(self):
        return "asdasd" # super(RollTableWorknode, self).__str__()

    def __repr__(self):
        return super(RollTableWorknode, self).__repr__()

    def do_my_work(self):
        self.additional_work.append(PerformRollWorknode(self.args.dice))


@dataclass
class PerformRollWorknode(NewWorkload):
    args: str   # Dice string
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.roll_for_table_outcome
    name: str = "Roll the dice"

    def __str__(self):
        return "asdasd" # super(PerformRollWorknode, self).__str__()

    def __repr__(self):
        return super(PerformRollWorknode, self).__repr__()

    def do_my_work(self):
        return dice.roll(self.args)


@dataclass
class RequestViaPrivateMessageWorknode(NewWorkload):
    args: Message
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.request_type_private_message
    name: str = "Request via PM"

    def __str__(self):
        return "asdasd" # super(RequestViaPrivateMessageWorknode, self).__str__()

    def __repr__(self):
        return super(RequestViaPrivateMessageWorknode, self).__repr__()

    def do_my_work(self):
        self.additional_work = [ParseForRedditDomainUrls(self.args),
                                ParseMessageWorknode(self.args)]


@dataclass
class ParseForRedditDomainUrls(NewWorkload):
    args: Union[Comment, Submission, Message]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_for_reddit_domain_urls
    name: str = "Search for Reddit urls"

    def __str__(self):
        return "asdasd" # super(ParseForRedditDomainUrls, self).__str__()

    def __repr__(self):
        return super(ParseForRedditDomainUrls, self).__repr__()

    def do_my_work(self):
        html_text = get_html_from_cms(self.args)
        reddit_links = get_links_from_text(html_text, 'reddit.com')

        if not reddit_links:
            return "No links found"

        for link in reddit_links:
            self.additional_work.append(FollowLinkWorknode(link))


@dataclass
class FollowLinkWorknode(NewWorkload):
    args: Tuple[str, str]  # text, href
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.follow_link
    name: str = "Consider following url"

    def __str__(self):
        return "asdasd" # super(FollowLinkWorknode, self).__str__()

    def __repr__(self):
        return super(FollowLinkWorknode, self).__repr__()

    def do_my_work(self):
        _, link_href = self.args
        reddit_item = Reddit.try_to_follow_link(link_href)
        if reddit_item is None:
            return "Refusing to follow non-Reddit link."

        self.additional_work = [ParseItemWorknode(reddit_item)]


@dataclass
class RequestViaUsernameMention(NewWorkload):
    args: Comment
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.request_type_username_mention
    name: str = "Request via username mention"

    def __str__(self):
        return "asdasd" # super(RequestViaUsernameMention, self).__str__()

    def __repr__(self):
        return super(RequestViaUsernameMention, self).__repr__()

    def do_my_work(self):
        # Until it is decided otherwise, a mention gets three actions:
        # (1) Look at the comment itself for a table
        # (2) Look for reddit-domain links to parse.
        # (2.1) Distinguish from links to submission (which also get top-level comments) and
        # (2.2) Comments, which maybe get the full treatment?
        # (3) Look at the OP
        # (4) Look at the top-level comments.
        mention = self.args
        op = mention.submission
        top_level_comments = list(op.comments)
        if mention in top_level_comments:
            top_level_comments.remove(mention)

        self.additional_work = [
            ParseCommentWorknode(mention),
            ParseForRedditDomainUrls(mention),
            ParseSubmissionWorknode(op),
            ParseTopLevelCommentsWorknode(top_level_comments)
        ]


if __name__ == '__main__':
    Reddit.login()
    pm = next(Reddit.r.inbox.messages())
    pm_node = RequestViaPrivateMessageWorknode(pm)
    pm_node.name = "test pm"
    pm_node.do_all_work()

    node_render = RenderTree(pm_node)
    shifted_node_render = " " * 4 + "\n    ".join(str(node_render).split("\n"))
    print(shifted_node_render)

