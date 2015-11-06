#!/usr/bin/env python3
import logging
import praw
from classes.reddit.context import MentionContext
from classes.util import configuration


class Reddit:
    r = None  # Static PRAW.Reddit reference

    def __init__(self):
        raise NotImplementedError("The Reddit class is not intended for instantiation.")

    @classmethod
    def login(cls):
        cls.r = praw.Reddit(user_agent=(
            'Generate an outcome for random tables, under the name'
            '/u/roll_one_for_me. Written and maintained by /u/PurelyApplied'),
            site_name="login_info")
        cls.r.login(disable_warning=True)

    @classmethod
    def logout(cls):
        del cls.r

    @staticmethod
    def beep_boop():
        """Builds and returns reply footer "Beep Boop I'm a bot...\""""
        s = "\n\n-----\n\n"
        s += ("*Beep boop I'm a bot.  " +
              "You can find usage and known issue details about me, as well as my source code, on " +
              "[GitHub](https://github.com/PurelyApplied/roll_one_for_me) page.  " +
              "I am maintained by /u/PurelyApplied.*\n\n"
              )
        s += "\n\n^(v{}; code base last updated {})".format(configuration.version, configuration.last_updated)
        return s

    @classmethod
    def get_mentions(cls) -> "user-mention generator":
        return cls.r.get_mentions()

    @classmethod
    def get_tables_from_mention(cls, mention):
        pass

    @classmethod
    def get_mention_context(cls, mention) -> MentionContext:
        logging.warning("get_mention_context is not implemented")
        return MentionContext({}, [])

if __name__ == "__main__":
    Reddit.login()
    pass
