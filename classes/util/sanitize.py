#!/usr/bin/env python3

from string import punctuation, whitespace

import logging

from classes.util.multimap import multimap


def sanitize(s: str):
    """Sanitizes some of the more commonly offensive string-handling issues:
    * Em- and En-dash to hyphen"""
    return "".join(multimap(s, unify_dashes, tabs_are_spaces))


def unify_dashes(s: str):
    """Replaces em- and en-dashes with hyphens."""
    return s.replace(u'\u2013', '-').replace(u'\u2014', '-')


def tabs_are_spaces(s: str, n=1):
    """Replaces tabs with n[=1 by default] spaces."""
    return s.replace("\t", n * " ")


def remove_mobile(s):
    """Replaces 'm.reddit.com' with 'reddit.com'"""
    logging.debug("Removing mobile 'm.'")
    return s.replace('m.reddit.com', 'reddit.com')


def remove_json(s):
    """Removes '.json' from the given string and prunes everything beyond."""
    logging.debug("Pruning .json and anything beyond.")
    return s[:s.find('.json')]


def ensure_www(s):
    """Adds 'www.' before 'reddit.com' if it is missing."""
    if 'reddit.com' in s and 'www.reddit.com' not in s:
        logging.debug("Injecting 'www.' to href")
        return s[:s.find("reddit.com")] + 'www.' + s[s.find("reddit.com"):]
    return s


def simplify_reddit_links(href: str):
    logging.debug("Sanitizing href: {}".format(href))
    # TODO: Multimap goes by character, so things like strip or searching for word blocks is bogus.
    sanitized = "".join(multimap([href],
                                 str.lower,
                                 str.strip,
                                 remove_json,
                                 remove_mobile,
                                 ensure_www,
                                 lambda x: x.rstrip("/")))
    logging.debug("Sanitized href: {}".format(sanitized))
    return sanitized


if __name__ == "__main__":
    s = u"This - is \u2013 \t\t\t gar \u2014 bag---e"
    href = r"m.reddit.com/BEEPBOOP/butts.json/"
    print("{}\n sanitized becomes\n{}".format(s, sanitize(s)))
    print("{}\n href-sanitized becomes\n{}".format(href, simplify_reddit_links(href)))