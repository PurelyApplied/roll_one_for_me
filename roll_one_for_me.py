#!/usr/bin/env python3

import logging
import logging.handlers
import time

from classes.reddit.endpoint import Reddit
from classes.util.configuration import Config, sloppy_config_load, Section, Subsection
from classes.util.decorators import static_vars, occasional


def main(config_file="config.ini"):
    Config(config_file)
    Reddit.login()
    while True:
        logging.debug("Beginning core loop.")
        answer_username_mentions()
        answer_private_messages()
        perform_sentinel_search()
        sleep()


@static_vars(interval=5)
def sleep():
    logging.info("Sleeping for {} seconds.".format(sleep.interval))
    time.sleep(sleep.interval)


@occasional(frequency=1)
def answer_username_mentions():
    mentions = Reddit.get_mentions()
    logging.info("Username mentions in this pass: {}".format(len(mentions)))
    for user_mention in mentions:
        answer_mention(user_mention)


def answer_mention(mention):
    context = Reddit.get_mention_context(mention)
    while context.stack:
        pass


@occasional(frequency=1)
def answer_private_messages():
    logging.info("PM functionality disabled.")
    pass


@occasional(counter=-1, frequency=10)
def perform_sentinel_search():
    logging.info("Sentinel functionality disabled.")
    pass


def update_static_variables():
    sleep.interval = int(Config.get(Section.sleep, Subsection.between_checks))


def configure_logging():
    logging_config = Config.get(Section.logging)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging_config.get(Subsection.level))

    formatter = logging.Formatter(logging_config.get(Subsection.format_string))
    formatter.datefmt = logging_config.get(Subsection.time_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging_config.get(Subsection.console_level))
    root_logger.addHandler(stream_handler)

    log_filename = Config.get(Section.logging, Subsection.filename)
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=log_filename, when='midnight', backupCount=90)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging_config.get(Subsection.level))
    root_logger.addHandler(file_handler)

if __name__ == "__main__":
    sloppy_config_load()
    configure_logging()
    logging.debug("Here's a debug message.")
    sleep()
    logging.debug("Again.")
    update_static_variables()
    sleep()
