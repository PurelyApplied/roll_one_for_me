#!/usr/bin/env python3

import logging
import logging.handlers
import time

from praw.models import Comment

from rofm.classes.reddit.endpoint import Reddit
from rofm.classes.util.configuration import Config, Section, Subsection
from rofm.classes.util.decorators import static_vars, occasional


def main(long_lived=True, config_file="config.ini"):
    Config(config_file)
    Reddit.login()
    first_pass = True
    while long_lived or first_pass:
        logging.debug("Begin core loop.")
        first_pass = False

        answer_username_mentions()
        answer_private_messages()
        perform_sentinel_search()

        heartbeat()
        sleep()


@occasional(frequency=15)
def heartbeat():
    logging.debug("A heart is beating and all is well.")
    pass


@static_vars(interval=5)
def sleep():
    logging.info("Sleeping for {} seconds.".format(sleep.interval))
    time.sleep(sleep.interval)


def answer_username_mentions():
    mentions = Reddit.get_mentions()
    logging.info("Username mentions in this pass: {}".format(len(mentions)))
    for user_mention in mentions:
        answer_mention(user_mention)


def answer_mention(mention: Comment):
    context = Reddit.get_mention_context(mention)
    while context.stack:
        pass


def answer_private_messages():
    logging.info("PM functionality disabled.")
    pass


@occasional(counter=-1, frequency=10)
def perform_sentinel_search():
    logging.info("Sentinel functionality disabled.")
    pass


def update_static_variables():
    interim = Config.get(Section.interim)
    sentinel = Config.get(Section.sentinel)

    sleep.interval = int(interim.get(Subsection.sleep_between_checks))
    heartbeat.frequency = int(interim.get(Subsection.passes_between_heartbeats))
    perform_sentinel_search.frequency = int(sentinel.get(Subsection.frequency))


if __name__ == "__main__":
    main()
