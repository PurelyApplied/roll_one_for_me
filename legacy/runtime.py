#!/usr/bin/python3

# Incoming messages will differentiate by type: Mentions are
# praw.objects.Comment.  PM will me praw.objects.Message.  (And OP
# items will be praw.objects.Submission)

# If a link is to a comment, get_submission resolves the OP with one
# comment (the actual comment linked), even if it is greater than one
# generation deep in comments.

# To add: Look for tables that are actual tables.
# Look for keyword ROLL in tables and scan for arbitrary depth

import logging
import os
import time

from praw.models import Message

import classes.util.configuration as future_configuration
from classes.reddit.endpoint import Reddit as FutureReddit
from legacy.models import Request, legacy_log
from roll_one_for_me import configure_logging as future_config_logging

##################
# Some constants #
##################
# TODO: This should be a config file.
_seen_max_len = 50
_fetch_limit = 25

_mentions_attempts = 10
_answer_attempts = 10

_sleep_on_error = 10
_sleep_between_checks = 60

_trivial_passes_per_heartbeat = 30


def main():
    future_configuration.sloppy_config_load()
    future_config_logging()
    legacy_log("Begin main()")
    while True:
        try:
            legacy_log("Signing into Reddit.")
            sign_in_to_reddit()
            while True:
                process_mail()
                legacy_log("Heartbeat.")
                time.sleep(_sleep_between_checks)
        except Exception as e:
            legacy_log("Top level.  Allowing to die for cron to revive.")
            legacy_log("Error: {}".format(e))
            raise e


def decline_private_messages():
    private_messages = FutureReddit.get_private_messages()
    pm = Message
    for pm in private_messages:
        apology = "I'm sorry.  PM parsing is currently borked.  I hope to have it up and running again soon."
        reply_text = apology + "\n\n" + beep_boop()
        pm.reply(reply_text)
        FutureReddit.r.inbox.mark_read((pm,))


def process_mail():
    decline_private_messages()
    my_mail = FutureReddit.get_mentions()
    to_process = [Request(x, FutureReddit.r) for x in my_mail]
    for item in to_process:
        if item.is_summons() or item.is_private_message():
            reply_text = item.roll()
            okay = True
            if not reply_text:
                reply_text = ("I'm sorry, but I can't find anything"
                              " that I know how to parse.\n\n")
                okay = False
            reply_text += beep_boop()
            if len(reply_text) > 10000:
                addition = ("\n\n**This reply would exceed 10000 characters"
                            " and has been shortened.  Chaining replies is an"
                            " intended future feature.")
                clip_point = 10000 - len(addition) - len(beep_boop()) - 200
                reply_text = reply_text[:clip_point] + addition + beep_boop()
            pass
            item.reply(reply_text)
            legacy_log("{} resolving request: {}.".format(
                "Successfully" if okay else "Questionably", item))
            if not okay:
                logging.error("Something bad happened in the 'not okay' block, but I don't log anymore.")
        else:
            logging.error("Mail was not summons or error, but I still don't log.  Marking as read anyway.")
        FutureReddit.r.inbox.mark_read((item.origin,))


def beep_boop():
    """Builds and returns reply footer "Beep Boop I'm a bot...\""""
    s = "\n\n-----\n\n"
    s += ("*Beep boop I'm a bot.*\n\n" +
          "*Sorry I've been away.  I had an API change, token decay, and my owner got hit by a car.  " +
          "We're both doing much better now.*\n\n" +
          "*You can find usage and known issue details about me, as well as my source code, on " +
          "[GitHub](https://github.com/PurelyApplied/roll_one_for_me) page.  " +
          "I am maintained by /u/PurelyApplied.*\n\n"
          )
    s += "\n\n^(v2.[-1].oh_god; code base last updated on a computer.  Probably both of those to update soon.)"
    return s


def sign_in_to_reddit():
    """Sign in to reddit using PRAW; returns Reddit handle"""
    FutureReddit.login()


def mail_util():
    """test(return_mentions=True)
    if return_mentions, returns tuple (reddit_handle, list_of_all_mail, list_of_mentions)
    else, returns tuple (reddit_handle, list_of_all_mail, None)
    """
    sign_in_to_reddit()
    all_mail = FutureReddit.get_unread()
    mentions = FutureReddit.get_mentions()
    return all_mail, mentions


####################
# Some testing items
_test_table = "https://www.reddit.com/r/DnDBehindTheScreen/comments/4aqi2l/fashion_and_style/"
# noinspection SpellCheckingInspection
_test_request = "https://www.reddit.com/r/DnDBehindTheScreen/comments/4aqi2l/fashion_and_style/d12wero"
T = "This has a d12 1 one 2 two 3 thr 4 fou 5-6 fiv/six 7 sev 8 eig 9 nin 10 ten 11 ele 12 twe"

if __name__ == "__main__":
    cwd = os.getcwd()
    if cwd.endswith("legacy"):
        os.chdir('..')
    print("Current working directory:", os.getcwd())
    main()
