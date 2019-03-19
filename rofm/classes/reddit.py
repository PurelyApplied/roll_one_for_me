#!/usr/bin/env python3
from typing import Union

import praw
from praw.exceptions import ClientException
from praw.models import Submission
from praw.models.reddit.comment import Comment
from praw.models.reddit.message import Message

from rofm.classes.util.decorators import with_class_logger

TIGHT_NEWLINE = "    \n"
WIDE_NEWLINE = "\n\n"


def comment_contains_username(comment: Comment):
    return Reddit.r.user.me().name in comment.body


@with_class_logger
class Reddit:
    # Static PRAW.reddit reference.  Define type for IDE integration.
    r: praw.Reddit = None

    def __init__(self):
        raise NotImplementedError("The reddit class is not intended for instantiation.")

    @classmethod
    def login(cls):
        cls.r = praw.Reddit(site_name="roll_one")

    @classmethod
    def logout(cls):
        del cls.r

    @classmethod
    def try_to_follow_link(cls, href) -> Union[Submission, Comment, None]:
        """A valid comment link can be resolved to the submission, but a submission cannot be resolved to comment.
        A client exception is thrown in this case, or if the URL leaves Reddit."""
        try:
            comment = cls.r.comment(url=href)
            cls.logger.debug(f"{href} resolved to comment.")
            return comment
        except ClientException as e:
            cls.logger.debug(f"Could not follow {href} as comment, ClientException: {e}")
            cls.logger.debug(f"Attempting to follow as submission")

        try:
            submission = cls.r.submission(url=href)
            cls.logger.debug(f"{href} resolved to submission.")
            return submission
        except ClientException as e:
            cls.logger.debug(f"Could not follow {href} as submission, ClientException: {e}")
            cls.logger.debug(f"Refusing to follow non-Reddit-domain link.")
            return None

    @classmethod
    def get_unread_mail(cls):
        return list(cls.r.inbox.unread())

    @classmethod
    def get_unread_username_mentions(cls) -> "user-mention generator":
        return [msg for msg in cls.r.inbox.unread() if isinstance(msg, Comment) and comment_contains_username(msg)]

    @classmethod
    def get_unread_private_messages(cls):
        # def get_private_messages(cls) -> List[Message]:
        return [msg for msg in cls.r.inbox.unread() if isinstance(msg, Message)]



if __name__ == "__main__":
    Reddit.login()
    pass
