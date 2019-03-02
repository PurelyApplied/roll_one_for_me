#!/usr/bin/env python3

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Union

from praw.models import Comment, Submission, Message

# noinspection PyMethodParameters
from rofm.classes.core.worknodes.core import Worknode, FollowLinkWorknode, WorkloadType
from rofm.classes.core.worknodes.rollers import TableWorknode
from rofm.classes.html_parsers import CMSParser, get_links_from_text
from rofm.classes.util.misc import get_html_from_cms

logging.getLogger().setLevel(logging.DEBUG)


@dataclass
class TopLevelCommentsWorknode(Worknode):
    args: List[Comment]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_top_level_comments
    _name: str = "Top level comment parser"

    def _my_work_resolver(self):
        for i, comment in enumerate(self.args):
            new_work = CommentWorknode(comment)
            new_work.metadata = {'index': i, 'source': 'Comment'}
            self.additional_work.append(new_work)

    def __str__(self):
        return "asdasd"  # super(ParseTopLevelCommentsWorknode, self).__str__()

    def __repr__(self):
        return super(TopLevelCommentsWorknode, self).__repr__()


@dataclass
class MixedTypeWorknode(Worknode):
    args: Union[Comment, Submission, Message]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_item_for_tables
    name: str = "Parse item of unidentified type"

    def __str__(self):
        return "asdasd"  # super(ParseItemWorknode, self).__str__()

    def __repr__(self):
        return super(MixedTypeWorknode, self).__repr__()

    def _my_work_resolver(self):
        parsed_tables = CMSParser(self.args, auto_parse=True).tables
        if not parsed_tables:
            return "No tables found"

        for table in parsed_tables:
            self.additional_work.append(TableWorknode(table))


@dataclass
class CommentWorknode(MixedTypeWorknode):
    args: Comment
    name: str = "Comment parser"

    def __repr__(self):
        return super(CommentWorknode, self).__repr__()


@dataclass
class SubmissionWorknode(MixedTypeWorknode):
    args: Submission
    name: str = "Submission parser"

    def __repr__(self):
        return super(SubmissionWorknode, self).__repr__()


@dataclass
class MessageWorknode(MixedTypeWorknode):
    args: Message
    name: str = "Private message parser"

    def __repr__(self):
        return super(MessageWorknode, self).__repr__()


@dataclass
class RedditDomainUrls(Worknode):
    args: Union[Comment, Submission, Message]
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.parse_for_reddit_domain_urls
    name: str = "Search for Reddit urls"

    def __str__(self):
        return "asdasd"  # super(ParseForRedditDomainUrls, self).__str__()

    def __repr__(self):
        return super(RedditDomainUrls, self).__repr__()

    def _my_work_resolver(self):
        html_text = get_html_from_cms(self.args)
        reddit_links = get_links_from_text(html_text, 'reddit.com')

        if not reddit_links:
            return "No links found"

        for link in reddit_links:
            self.additional_work.append(FollowLinkWorknode(link))
