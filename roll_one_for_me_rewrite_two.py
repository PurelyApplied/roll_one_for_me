#!/usr/bin/env python3

import logging
import logging.handlers
import time

from rofm.classes.core.worknodes.workload import WorkNode, WorkloadType
from rofm.classes.reddit import Reddit
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
    mentions = Reddit.get_unread_username_mentions()
    logging.info("Username mentions in this pass: {}".format(len(mentions)))
    for user_mention in mentions:
        this_mention_workload = WorkNode(WorkloadType.request_type_username_mention,
                                         user_mention,
                                         name=f"Mention from {user_mention.author}")
        this_mention_workload.do_all_work()
        user_mention.reply(this_mention_workload.get_response_text())


def answer_private_messages():
    logging.info("PM functionality disabled.")
    pass


def update_static_variables():
    interim = Config.get(Section.interim)

    sleep.interval = int(interim.get(Subsection.sleep_between_checks))
    heartbeat.frequency = int(interim.get(Subsection.passes_between_heartbeats))


if __name__ == "__main__":
    main()
