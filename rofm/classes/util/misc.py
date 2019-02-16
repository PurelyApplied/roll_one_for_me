#!/usr/bin/env python3
from typing import Union

from praw.models import Comment, Submission, Message


def prompt_for_yes_no(prompt_string, default=None):
    """Prompts for "yes" or "no" and returns True or False respectively."""
    valid = {'yes': True, 'ye': True, 'y': True,
             'no': False, 'n': False}

    if default is not None:
        assert isinstance(default, bool), "Use the desired boolean return value for parameter 'default'"
        valid[''] = default

    while True:
        choice = input(prompt_string).strip().lower()
        if choice in valid:
            return valid[choice]
        print("Please respond with 'yes' or 'no'\n")


def get_text_from_comment_submission_or_message(obj: Union[Comment, Submission, Message], get_html=False):
    if isinstance(obj, Comment) or isinstance(obj, Message):
        return obj.body_html if get_html else obj.body
    if isinstance(obj, Submission):
        return obj.selftext_html if get_html else obj.selftext
    raise TypeError(f"Expected Comment, Submission, or Message in {__name__}")


def split_iterable(iterable, split_condition):
    list_satisfying = []
    list_not_satisfying = []
    for item in iterable:
        if split_condition(item):
            list_satisfying.append(item)
        else:
            list_not_satisfying.append(item)
    return list_satisfying, list_not_satisfying


if __name__ == '__main__':
    prompt_for_yes_no("test case. > ")
