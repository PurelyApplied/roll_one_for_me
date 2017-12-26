#!/usr/bin/env python3


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

if __name__ == '__main__':
    prompt_for_yes_no("test case. > ")
