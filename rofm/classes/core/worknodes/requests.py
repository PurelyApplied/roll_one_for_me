from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any

from praw.models import Comment, Message

# noinspection PyMethodParameters
from rofm.classes.core.worknodes.core import Worknode, WorkloadType
from rofm.classes.core.worknodes.parsers import (RedditDomainUrls, MessageWorknode, CommentWorknode,
                                                 SubmissionWorknode, TopLevelCommentsWorknode)


@dataclass
class PMWorknode(Worknode):
    args: Message
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.request_type_private_message
    name: str = "Request via PM"

    def __str__(self):
        return "asdasd"  # super(RequestViaPrivateMessageWorknode, self).__str__()

    def __repr__(self):
        return super(PMWorknode, self).__repr__()

    def _my_work_resolver(self):
        self.additional_work = [RedditDomainUrls(self.args),
                                MessageWorknode(self.args),
                                MessageWorknode(self.args),
                                ]


@dataclass
class MentionWorknode(Worknode):
    args: Comment
    kwargs: Dict[str, Any] = field(default_factory=dict)

    workload_type: WorkloadType = WorkloadType.request_type_username_mention
    name: str = "Request via username mention"

    def __str__(self):
        return "asdasd"  # super(RequestViaUsernameMention, self).__str__()

    def __repr__(self):
        return super(MentionWorknode, self).__repr__()

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
            CommentWorknode(mention),
            RedditDomainUrls(mention),
            SubmissionWorknode(op),
            TopLevelCommentsWorknode(top_level_comments)
        ]
