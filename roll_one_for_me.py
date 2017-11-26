#!/usr/bin/env python3

import logging
from classes.reddit.endpoint import Reddit
from classes.util.configuration import Config, get_version_and_updated, Section, Subsection
import time

from classes.util.decorators import static_vars


def main(config_file="config.ini"):
    Config(config_file)
    Reddit.login()
    while True:
        logging.debug("Beginning core loop.")
        answer_username_mentions()
        answer_private_messages()
        perform_sentinel_search()
        sleep()


@static_vars(inverval=5)
def sleep():
    logging.debug("Sleeping for {} seconds.".format(sleep.interval))
    time.sleep(sleep.interval)


@static_vars(counter=0)
def answer_username_mentions():
    mentions = Reddit.get_mentions()
    logging.info("Username mentions in this pass: {}".format(len(mentions)))
    for user_mention in mentions:
        answer_mention(user_mention)


@static_vars(counter=0)
def answer_mention(mention):
    context = Reddit.get_mention_context(mention)
    while context.stack:
        pass


@static_vars(counter=0)
def answer_private_messages():
    logging.info("PM functionality disabled.")
    pass


@static_vars(counter=0)
def perform_sentinel_search():
    logging.info("Sentinel functionality disabled.")
    pass


if __name__ == "__main__":
    Config()
    print(get_version_and_updated())
    print("bye")
    main()
