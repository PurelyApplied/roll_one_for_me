#!/usr/bin/python3
"""Implementation for reddit bot /u/roll_one_for_me.

Bot usage: summon with user mention to /u/roll_one_for_me, or send a
private message.

Default behavior: Summoning text / private message is parsed for
tables and links to tables.  If called using a user-mention, the
original post and top-level comments are also scanned.

Each table is parsed and rolled, and a reply is given.

Tables must begin with a die notation starting a newline (ignoring
punctuation).

"""


# TODO: I have a lot of generic 'except:' catches that should be specified to error type.  I need to learn PRAW's
# error types.

import configparser
import logging
import os
import time

from rofm_bot import RollOneForMe

from archive import dice

logging_level = logging.INFO
_trivial_passes_per_heartbeat = 20

# Make sure you're in the correct local directory.
try:
    full_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(full_path)
    os.chdir(root_dir)
except:
    pass


# As a function for live testing, as opposed to the one-line in main()
def prepare_logger(this_logging_level=logging.INFO,
                   other_logging_level=logging.ERROR,
                   log_filename=None,
                   log_file_mode='a',
                   format_string=None):
    """Clears the logging root and creates a new one to use, setting basic
config."""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=other_logging_level,
                        format=format_string)
    for my_module in ('rofm_bot', 'dice', 'tables', ''):
        logging.getLogger(my_module).setLevel(this_logging_level)
    if log_filename:
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(this_logging_level)
        file_handler.setFormatter(logging.Formatter(format_string))
        logging.getLogger().addHandler(file_handler)

    
def config_test():
    conf = configparser.RawConfigParser()
    conf.read("config.ini")
    try:
        configurate(conf)
    except:
        pass
    return conf


def configurate(config):
    # Dice
    d_conf = config['dice']
    dice.set_limits(
        int(d_conf['max_n']),
        int(d_conf['max_k']),
        int(d_conf['max_compound_roll_length']))
    # IO
    io_conf = config['io']
    prepare_logger(
        getattr(logging, io_conf['my_log_level']),
        getattr(logging, io_conf['external_log_level']),
        io_conf['log_filename'],
        io_conf['log_file_mode'],
        io_conf['log_format_string'])


def main(config_file,
         this_logging_level=logging.INFO,
         other_logging_level=logging.ERROR,
         ):
    """Logs into reddit, looks for unanswered user mentions, and
    generates and posts replies"""
    # Initialize
    prepare_logger(logging_level)
    config = configparser.RawConfigParser()
    config.read(config_file)
    configurate(config)
    logging.info("Initializing rofm.")
    rofm = RollOneForMe()
    trivial_passes_count = 0
    logging.info("Enter core loop.")
    trivial_per_heartbeat = config['io']['n_trivial_passes_per_heartbeat']
    while True:
        try:
            rofm.act()
            trivial = rofm.end_of_pass()
        except:
            trivial = False
            pass
        finally:
            trivial_passes_count = (
                0 if not trivial
                else trivial_passes_count + 1)
            if trivial_passes_count == trivial_per_heartbeat:
                logging.info(
                    "{} passes without incident.".format(
                        _trivial_passes_per_heartbeat))
                trivial_passes_count = 0
            time.sleep(int(config['sleep']['between_checks']))

####################


def configtest():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config


def dbg():
    prepare_logger(logging.DEBUG)

