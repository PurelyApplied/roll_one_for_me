#!/usr/bin/env python3
import logging
from typing import List

import praw
from praw.exceptions import PRAWException

from classes.reddit.context import MentionContext
from classes.util import configuration

from praw.models.reddit.comment import Comment
from praw.models.reddit.message import Message


def comment_contains_username(comment: Comment):
    return Reddit.r.user.me().name in comment.body


class Reddit:
    # Static PRAW.reddit reference.  Define type for IDE integration.
    r = praw.Reddit(client_id="void", user_agent="void", client_secret="void")

    def __init__(self):
        raise NotImplementedError("The reddit class is not intended for instantiation.")

    @classmethod
    def login(cls):
        cls.r = praw.Reddit(user_agent=(
            'Generate an outcome for random tables, under the name'
            '/u/roll_one_for_me. Written and maintained by /u/PurelyApplied'),
            site_name="roll_one")

    @classmethod
    def logout(cls):
        del cls.r

    @staticmethod
    def beep_boop():
        """Builds and returns reply footer "Beep Boop I'm a bot...\""""
        s = "\n\n-----\n\n"
        s += ("*Beep boop I'm a bot.\n\n"
              "Sorry I've been gone for a while.  "
              "I got hit with some API changes and maybe some OAuth token decay "
              "around the same time my author got hit by a car.  "
              "We're both doing much better now, though.\n\n"
              "You can find usage and known issue details about me, as well as my source code, on "
              "[GitHub](https://github.com/PurelyApplied/roll_one_for_me) page.  "
              "I am written and maintained by /u/PurelyApplied.*\n\n"
              )
        s += "\n\n^(v{}; code base last updated {})".format(*configuration.get_version_and_updated())
        return s

    @classmethod
    def get_unread(cls):
        return list(cls.r.inbox.unread())

    @classmethod
    def get_mentions(cls) -> "user-mention generator":
        return [msg for msg in cls.r.inbox.unread() if isinstance(msg, Comment) and comment_contains_username(msg)]

    @classmethod
    def get_private_messages(cls) -> List[Message]:
        return [msg for msg in cls.r.inbox.unread() if isinstance(msg, Message)]

    @classmethod
    def get_tables_from_mention(cls, mention):
        pass

    @classmethod
    def get_mention_context(cls, mention) -> MentionContext:
        logging.warning("get_mention_context is not implemented")
        return MentionContext({}, [])

    @classmethod
    def try_to_follow_link(cls, href):
        try:
            logging.debug("Attempting to follow href to comment: {}".format(href))
            return cls.r.comment(href)
        except PRAWException:
            logging.debug("Comment failed.  Attempting to follow href to submission: {]".format(href))
            return cls.r.submission(None, href)


if __name__ == "__main__":
    Reddit.login()
    pass
