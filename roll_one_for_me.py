#!/usr/bin/env python3

import logging
from classes.reddit.endpoint import Reddit


def main():
    load_configuration()
    Reddit.login()
    while True:
        answer_username_mentions()
        answer_private_messages()
        perform_sentinel_search()


def answer_username_mentions():
    mentions = Reddit.get_mentions()
    logging.info("Username mentions in this pass: {}".format(len(mentions)))
    for user_mention in mentions:
        answer_mention(user_mention)


def answer_mention(mention):
    context = Reddit.get_mention_context(mention)


def answer_private_messages():
    logging.info("PM functionality disabled.")
    pass


def perform_sentinel_search():
    logging.info("Sentinel functionality disabled.")
    pass


def load_configuration():
    logging.getLogger('').setLevel(logging.DEBUG)
    logging.info("load_configuration not implemented.")

if __name__ == "__main__":
    pass
