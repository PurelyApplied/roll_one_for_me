#!/usr/bin/env python3
import logging

import praw
from praw.models.reddit.comment import Comment
from praw.models.reddit.message import Message


def comment_contains_username(comment: Comment):
    return Reddit.r.user.me().name in comment.body


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
    def get_unread_mail(cls):
        return list(cls.r.inbox.unread())

    @classmethod
    def get_unread_username_mentions(cls) -> "user-mention generator":
        return [msg for msg in cls.r.inbox.unread() if isinstance(msg, Comment) and comment_contains_username(msg)]

    @classmethod
    def get_unread_private_messages(cls):
        # def get_private_messages(cls) -> List[Message]:
        return [msg for msg in cls.r.inbox.unread() if isinstance(msg, Message)]

    @classmethod
    def try_to_follow_link(cls, href):
        try:
            logging.debug("Attempting to follow href to comment: {}".format(href))
            return cls.r.comment(href)
        except praw.exceptions.PRAWException:
            logging.debug("Could not follow link as comment.  Attempting to follow href to submission: {]".format(href))
            return cls.r.submission(None, href)


if __name__ == "__main__":
    Reddit.login()
    pass
