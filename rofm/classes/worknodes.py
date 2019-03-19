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
from typing import Dict, Tuple, Optional, List, Any, Union

import dice
import praw.models
from anytree import NodeMixin, PreOrderIter, RenderTree
from praw.models import Comment, Submission, Message

from rofm.classes.html_parsers import CMSParser, get_links_from_text
from rofm.classes.reddit import Reddit, TIGHT_NEWLINE, WIDE_NEWLINE
from rofm.classes.tables import Table
from rofm.classes.util.misc import get_html_from_cms

logging.getLogger().setLevel(logging.DEBUG)


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class WorkloadType(str, AutoName):
    """Every Workload / WorkNode should refer to a definitive type to determine behavior."""
    # This may now be a deprecated concept, supplanted by better class definitions in WorkNodes.

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
        in_as_string += self.get_display_args()
        in_as_string += ',' if self.args and self.kwargs else ''
        in_as_string += self.get_display_kwargs()
        in_as_string += ')'

        out_as_string = self.get_display_output_or_exception()

        return f"<{display_name} :: {in_as_string} {out_as_string}>"

    def get_display_output_or_exception(self):
        return (f"-> !! threw {self.exception}"
                if self.exception else
                f"-> {self.output}" if self.output else "")

    def get_display_kwargs(self):
        return f"{self.kwargs}" if self.kwargs else ''

    def get_display_args(self):
        return f"{self.args}" if self.args else ''

    def _almost_repr(self):
        return repr(self).strip("'")


@dataclass
class TopLevelComments(Worknode):
    args: List[Comment]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_top_level_comments
    _name: str = "Top level comment parser"

    def _my_work_resolver(self):
        for i, comment in enumerate(self.args):
            new_work = Comment(comment)
            new_work.metadata = {'index': i, 'source': 'Comment'}
            self.additional_work.append(new_work)

    def __str__(self):
        return "\n\n\n".join((str(work) for work in self.additional_work if str(work)))

    def __repr__(self):
        return super(TopLevelComments, self).__repr__()

    def get_display_args(self):
        return "<Comments: [" + ", ".join(str(c.id) for c in self.args) + "]>"


@dataclass
class MixedType(Worknode):
    args: Union[Comment, Submission, Message]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_item_for_tables
    name: str = "Parse item of unidentified type"

    def __str__(self):
        return f"{WIDE_NEWLINE}-----{WIDE_NEWLINE}".join(str(c) for c in self.children)

    def __repr__(self):
        return super(MixedType, self).__repr__()

    def _my_work_resolver(self):
        parsed_tables = CMSParser(self.args, auto_parse=True).tables
        if not parsed_tables:
            return "No tables found"

        for table in parsed_tables:
            self.additional_work.append(RollTable(table))


@dataclass
class Comment(MixedType):
    args: Comment
    name: str = "Comment parser"

    def __str__(self):
        return super(Comment, self).__str__()

    def __repr__(self):
        return super(Comment, self).__repr__()


@dataclass
class Submission(MixedType):
    args: Submission
    name: str = "Submission parser"

    def __str__(self):
        return super(Submission, self).__str__()

    def __repr__(self):
        return super(Submission, self).__repr__()


@dataclass
class Message(MixedType):
    args: Message
    name: str = "Private message parser"

    def __str__(self):
        return super(Message, self).__str__()

    def __repr__(self):
        return super(Message, self).__repr__()


@dataclass
class RedditDomainUrls(Worknode):
    args: Union[Comment, Submission, Message]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_for_reddit_domain_urls
    name: str = "Search for Reddit urls"

    def __str__(self):
        return "\n\n\n".join((str(work) for work in self.additional_work if str(work)))

    def __repr__(self):
        return super(RedditDomainUrls, self).__repr__()

    def _my_work_resolver(self):
        html_text = get_html_from_cms(self.args)
        reddit_links = get_links_from_text(html_text, 'reddit.com')

        if not reddit_links:
            return "No links found"

        for link in reddit_links:
            self.additional_work.append(FollowLink(link))


@dataclass
class SpecialRequest(Worknode):
    args: Union[Comment, Submission, Message]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_for_special_requests
    name: str = "Search for special requests"

    def __str__(self):
        return "Not yet implemented"

    def __repr__(self):
        return super(SpecialRequest, self).__repr__()

    def _my_work_resolver(self):
        raise NotImplementedError("Special requests not yet implemented.")


@dataclass
class FollowLink(Worknode):
    args: Tuple[str, str]  # text, href
    kwargs: Dict[str, Any] = field(default_factory=dict)

    # populated in post-init
    text: str = None
    href: str = None

    workload_type: WorkloadType = WorkloadType.follow_link
    name: str = "Consider following url"

    def __post_init__(self):
        self.text, self.href = self.args

    def __str__(self):
        if self.additional_work:
            return f"#####From your link [{self.text}]({self.href}):\n\n{self.additional_work[0]}"
        return (f"Your link [{self.text}]({self.href}] doesn't resolve for me, possibly because it's not on Reddit."
                f"  I don't like to wander too far from home, sorry.")

    def __repr__(self):
        return super(FollowLink, self).__repr__()

    def _my_work_resolver(self):
        _, link_href = self.args
        reddit_item = Reddit.try_to_follow_link(link_href)
        if reddit_item is None:
            return "Refusing to follow non-Reddit link."

        self.additional_work = [MixedType(reddit_item)]


@dataclass
class Request(Worknode, ABC):
    args: Union[praw.models.Message, praw.models.Comment]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.request_type_private_message
    name: str = "Request via PM"

    def get_response_text(self, with_work_trace=False):
        if not with_work_trace:
            return f"{self}{WIDE_NEWLINE}{self.beep_boop()}"

        return f"{self}{WIDE_NEWLINE}{self.beep_boop()}{TIGHT_NEWLINE}{self.humble_brag()}"

    def __str__(self):
        """Core response text, not including the bot tag."""
        return f"{WIDE_NEWLINE}-----{WIDE_NEWLINE}".join((str(work) for work in self.children if str(work)))

    def __repr__(self):
        return super(Request, self).__repr__()

    def beep_boop(self):
        return (f"*Beep boop, I'm a bot.*{TIGHT_NEWLINE}"
                f"*I am maintained by /u/PurelyApplied,"
                f" for whom these username mentions are a huge morale boost.*{TIGHT_NEWLINE}"
                f"*You can find my source code and more details about me"
                f" on [GitHub](https://github.com/PurelyApplied/roll_one_for_me).*"
                )

    def humble_brag(self):
        return (f"*The following is the work I did for you!"
                f"  I'm posting it for now for easier debugging and a little bot humble-bragging.*{WIDE_NEWLINE}"
                f"{self.get_most_of_render_tree()}"
                )

    def get_most_of_render_tree(self):
        # Use __repr__ so that this isn't recursive, and also since it's just for debugging.
        # But then strip the quotes so we don't get " '<Roll table :: ...'"

        # We also don't dump any top-level-comments that don't make the cut, so we're not spamming in the footer.

        #  These are Worknodes, but RenderTree doens't realize that.
        # noinspection PyProtectedMember
        return "\n".join(f"    {pre}{worknode._almost_repr()}"
                         for pre, _, worknode in (RenderTree(self))
                         if not isinstance(worknode, Comment) or worknode.children)


@dataclass
class PrivateMessage(Request):
    args: praw.models.Message
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.request_type_private_message
    name: str = "Request via PM"

    def __str__(self):
        return super(PrivateMessage, self).__str__()

    def __repr__(self):
        return super(PrivateMessage, self).__repr__()

    def _my_work_resolver(self):
        self.additional_work = [
            RedditDomainUrls(self.args),
            Message(self.args),
            SpecialRequest(self.args)
        ]


@dataclass
class UsernameMention(Request):
    args: praw.models.Comment
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.request_type_username_mention
    name: str = "Request via username mention"

    def __str__(self):
        return super(UsernameMention, self).__str__()

    def __repr__(self):
        return super(UsernameMention, self).__repr__()

    def _my_work_resolver(self):
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
            Comment(mention),
            RedditDomainUrls(mention),
            Submission(op),
            TopLevelComments(top_level_comments)
        ]


@dataclass
class RollAny(Worknode):
    args: str  # Dice string
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.roll_for_table_outcome
    name: str = "Roll the dice"

    def __str__(self):
        return "RollAny not expected to be posted directly.  Fetch value from output."

    def __repr__(self):
        return super(RollAny, self).__repr__()

    def _my_work_resolver(self):
        return dice.roll(self.args)


@dataclass
class RollTable(Worknode):
    args: Table
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.roll_table
    name: str = "Roll table"

    def __str__(self):
        # A rolled table should have one child holding the value.
        rolled_value = int(self.children[0].output)
        return f"{self.args.description}:    \n{self.args.dice} -> {rolled_value}: {self.args.get(rolled_value)}\n\n\n"

    def __repr__(self):
        return super(RollTable, self).__repr__()

    def _my_work_resolver(self):
        self.additional_work.append(RollAny(self.args.dice))
