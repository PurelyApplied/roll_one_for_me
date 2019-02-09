#!/usr/bin/env python3

import logging
import logging.handlers
import time

from rofm.classes.reddit import Reddit
from rofm.classes.util.configuration import Config
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
    logging.info(f"Sleeping for {sleep.interval} seconds.")
    time.sleep(sleep.interval)


def answer_username_mentions():
    mentions = Reddit.get_unread_username_mentions()

    logging.info(f"Username mentions in this pass: {len(mentions)}")
    for user_mention in mentions:
        pass
        # answer_mention(user_mention)


if __name__ == "__main__":
    main()
