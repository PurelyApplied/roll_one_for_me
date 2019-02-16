import configparser
import logging
import logging.handlers
import os.path
from enum import Enum
from os import path

from rofm.classes.util.misc import prompt_for_yes_no


class Config:
    """Singleton container wrapping configparser calls."""
    config = configparser.ConfigParser()
    files_loaded = []

    @classmethod
    def __init__(cls, *in_files, clear_before_load=False):
        if clear_before_load:
            cls.config.clear()
            cls.files_loaded = []

        for f in in_files:
            cls.load_file(f)

    @classmethod
    def __str__(cls):
        # noinspection SpellCheckingInspection
        fillable = ", ".join(["{!r}"] * len(cls.files_loaded))
        return "Config({})".format(fillable.format(*cls.files_loaded))

    @classmethod
    def clear(cls):
        cls.config.clear()
        cls.files_loaded = []

    @classmethod
    def get(cls, *items):
        c = cls.config
        for item in items:
            c = c[item]
        return c

    def __getitem__(self, item):
        return self.config[item]

    @classmethod
    def load_file(cls, f):
        if not path.exists(f):
            raise FileNotFoundError("Cannot find configuration file '{}'.".format(f))
        cls.files_loaded.append(f)
        cls.config.read(f)


class Section(str, Enum):
    """Enum specifying required keys for config.ini"""
    version = "version"
    sentinel = "sentinel"
    interim = "interim"
    logging = "logging"
    dice = "dice"
    links = "links"
    attempts = "attempts"


# noinspection SpellCheckingInspection
class Subsection(str, Enum):
    """Enum specifying required subsection keys for config.ini"""
    # Version
    major = "major"
    minor = "minor"
    patch = "patch"
    last_updated = "last_updated"
    # sentinel
    fetch_limit = "fetch_limit"
    seen_cache = "seen_cache"
    frequency = "frequency"
    # interim
    sleep_between_attempts = "sleep_between_attempts"
    sleep_between_checks = "sleep_between_checks"
    passes_between_heartbeats = "passes_between_heartbeats"
    # attempts
    per_user_mention = "per_user_mention"
    per_answer_attempt = "per_answer_attempt"
    log_in = "log_in"
    # logging
    rofm_level = "rofm_level"
    requests_level = "requests_level"
    prawcore_level = "prawcore_level"
    file_log_level = "file_log_level"
    console_level = "console_level"
    logs_directory = "logs_directory"
    filename = "filename"
    format_string = "format_string"
    time_format = "time_format"
    max_filesize = "max_filesize"
    backup_count = "backup_count"
    passes_per_heartbeat = "passes_per_heartbeat"
    # dice
    max_n = "max_n"
    max_k = "max_k"
    max_compound_roll_length = "max_compound_roll_length"
    # links
    max_depth = "max_depth"


def get_version_and_updated():
    info = Config()[Section.version]
    major = info.get("major")
    minor = info.get("minor")
    patch = info.get("patch")
    version_string = "{}.{}.{}".format(major, minor, patch)
    return version_string, Config.get(Section.version, Subsection.last_updated)


def configure_logging():
    logging_config = Config.get(Section.logging)
    root_logger = logging.getLogger()
    set_log_levels(logging_config)

    formatter = logging.Formatter(logging_config.get(Subsection.format_string))
    formatter.datefmt = logging_config.get(Subsection.time_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging_config.get(Subsection.console_level))
    root_logger.addHandler(stream_handler)

    logs_directory = Config.get(Section.logging, Subsection.logs_directory)
    if not os.path.exists(logs_directory):
        if prompt_for_yes_no("Attempt to create logs directory '{}'? (current working directory: '{}')  > ".format(logs_directory, os.getcwd())):
            os.mkdir(logs_directory)
        else:
            raise FileNotFoundError("Please create your logs directory: '{}'".format(logs_directory))
    elif not os.path.isdir(logs_directory):
        raise FileExistsError("Non-directory file '{}' already exists.".format(logs_directory))

    log_filename = logs_directory + os.sep + Config.get(Section.logging, Subsection.filename)
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=log_filename, when='midnight', backupCount=90)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging_config.get(Subsection.file_log_level))
    root_logger.addHandler(file_handler)


# noinspection SpellCheckingInspection
def set_log_levels(logging_config):
    root = logging.getLogger()
    rofm = logging.getLogger("roll_one_for_me")
    requests = logging.getLogger("requests")
    prawcore = logging.getLogger("prawcore")

    root.setLevel(logging.DEBUG)
    rofm.setLevel(logging_config.get(Subsection.rofm_level))
    requests.setLevel(logging_config.get(Subsection.requests_level))
    prawcore.setLevel(logging_config.get(Subsection.prawcore_level))