#!/usr/bin/env python3

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Union

from praw.models import Comment, Submission, Message

# noinspection PyMethodParameters
from rofm.classes.core.worknodes.core import NewWorkload, FollowLinkWorknode, WorkloadType
from rofm.classes.core.worknodes.rollers import RollTableWorknode
from rofm.classes.html_parsers import CMSParser, get_links_from_text
from rofm.classes.util.misc import get_html_from_cms

logging.getLogger().setLevel(logging.DEBUG)


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
        return "asdasd"  # super(ParseTopLevelCommentsWorknode, self).__str__()

    def __repr__(self):
        return super(ParseTopLevelCommentsWorknode, self).__repr__()


@dataclass
class ParseItemWorknode(NewWorkload):
    args: Union[Comment, Submission, Message]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_item_for_tables
    name: str = "Parse item of unidentified type"

    def __str__(self):
        return "asdasd"  # super(ParseItemWorknode, self).__str__()

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
class ParseForRedditDomainUrls(NewWorkload):
    args: Union[Comment, Submission, Message]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_for_reddit_domain_urls
    name: str = "Search for Reddit urls"

    def __str__(self):
        return "asdasd"  # super(ParseForRedditDomainUrls, self).__str__()

    def __repr__(self):
        return super(ParseForRedditDomainUrls, self).__repr__()

    def do_my_work(self):
        html_text = get_html_from_cms(self.args)
        reddit_links = get_links_from_text(html_text, 'reddit.com')

        if not reddit_links:
            return "No links found"

        for link in reddit_links:
            self.additional_work.append(FollowLinkWorknode(link))
