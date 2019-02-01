#!/usr/bin/env python3

# Incoming messages will differentiate by type: Mentions are
# praw.objects.Comment.  PM will me praw.objects.Message.  (And OP
# items will be praw.objects.Submission)

# If a link is to a comment, get_submission resolves the OP with one
# comment (the actual comment linked), even if it is greater than one
# generation deep in comments.

# To add: Look for tables that are actual tables.
# Look for keyword ROLL in tables and scan for arbitrary depth
import logging
import time

from .models import Request
from ..classes.reddit.endpoint import Reddit as FutureReddit
from ..classes.util import configuration as future_configuration
import google.cloud.logging


def main(long_lived=True, config_file="config.ini"):
    future_configuration.Config(config_file)
    google.cloud.logging.Client().setup_logging()
    future_configuration.configure_logging()

    logging.debug("Configuration loaded: '{}'.".format(future_configuration.Config()))
    sleep_between_checks = int(future_configuration.Config.get(future_configuration.Section.interim,
                                                               future_configuration.Subsection.sleep_between_checks))
    logging.debug("Begin main()")
    try:
        logging.debug("Signing into Reddit.")
        sign_in_to_reddit()
        while True:
            process_mail()
            if not long_lived:
                logging.debug("Not run with --long-lived.  Exiting.")
                return
            logging.debug("Heartbeat.")
            time.sleep(sleep_between_checks)
    except Exception as e:
        logging.debug("Top level.  Allowing to die for cron to revive.")
        logging.debug("Error: {}".format(e))
        raise e


def decline_private_messages():
    apology = "I'm sorry.  PM parsing is currently borked."
    apology += "  But look!  I'm alive again.  So that's promising, after all this time."
    apology += "  Maybe PMs will get some love soon."
    apology += "  Or maybe that re-write that my human has been meaning to do will actually get done."
    apology += "  Here's to hoping."
    reply_text = apology + "\n\n" + beep_boop()

    private_messages = FutureReddit.get_private_messages()
    for pm in private_messages:
        logging.info("Replying to {} with an apology declining to answer their PM.".format(pm.author))
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
            logging.debug("{} resolving request: {}.".format(
                "Successfully" if okay else "Questionably", item))
            if not okay:
                logging.error("Something bad happened in the 'not okay' block, but I don't log anymore.")
        else:
            logging.error("Mail was not summons or error, but I still don't log.  Marking as read anyway.")
        FutureReddit.r.inbox.mark_read((item.origin,))


def beep_boop():
    """Builds and returns reply footer "Beep Boop I'm a bot...\""""
    s = "\n\n-----\n\n"
    s += ("*Beep boop I'm a bot.  And I live... AGAIN!*\n\n" +
          "*Sorry about my human letting me go dark for almost a year.  What a dingus.*\n\n"
          "*I should be long-lived and fast to respond again, though.  Although PMing is still borked.*\n\n"
          "*But hey.  New features (and the old ones again, too) coming soon,"
          " since my human is trying to refresh his resume and portfolio.*\n\n"
          "*As ever, you can maybe find usage and known issue details about me, as well as my source code, on "
          "[GitHub](https://github.com/PurelyApplied/roll_one_for_me) page.  " +
          "I am maintained by /u/PurelyApplied, the dingus.*\n\n"
          )
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
