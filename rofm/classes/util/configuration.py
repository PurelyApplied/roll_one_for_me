import configparser
import logging
from enum import Enum
from os import path


class Config:
    """Singleton container wrapping configparser calls."""
    config = configparser.ConfigParser()

    def __init__(self, in_file=None, clear_before_load=True):
        self.in_file = in_file
        self.cleared_before_loading = clear_before_load

        logging.debug("Loading configuration: {}".format(self))
        if not path.exists(in_file):
            raise FileNotFoundError("Cannot find configuration file '{}' in the path.".format(in_file))
        if clear_before_load:
            self.clear()
        self.config.read(in_file)

    def __str__(self):
        return "Config({}, {})".format(self.in_file, self.cleared_before_loading)

    @classmethod
    def clear(cls):
        cls.config.clear()

    @classmethod
    def get(cls, *items):
        c = cls.config
        for item in items:
            c = c[item]
        return c

    def __getitem__(self, item):
        return self.config[item]


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


# noinspection SpellCheckingInspection
def sloppy_config_load():
    # It should be somewhere on the path.  Later, I'll pass it as a parameter properly.
    Config(r"config.ini")
