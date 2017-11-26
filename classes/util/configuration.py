import configparser
from enum import Enum
from os import path

import roll_one_for_me


class Section(str, Enum):
    """Enum specifying required keys for config.ini"""
    version = "version"
    sentinel = "sentinel"
    sleep = "sleep"
    logging = "logging"
    dice = "dice"
    links = "links"


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
    # sleep
    between_attempts = "between_attempts"
    between_checks = "between_checks"
    # attempts
    per_user_mention = "per_user_mention"
    per_answer_attempt = "per_answer_attempt"
    log_in = "log_in"
    # logging
    internal_level = "internal_level"
    external_level = "external_level"
    filename = "filename"
    format_string = "format_string"
    max_filesize = "max_filesize"
    backup_count = "backup_count"
    passes_per_heartbeat = "passes_per_heartbeat"
    # dice
    max_n = "max_n"
    max_k = "max_k"
    max_compound_roll_length = "max_compound_roll_length"
    # links
    max_depth = "max_depth"


class Config:
    """Singleton container wrapping configparser calls."""
    config = configparser.ConfigParser()

    def __init__(self, in_file=None, clear_before_load=True):
        if not in_file:
            return
        if not path.exists(in_file):
            raise FileNotFoundError("Cannot find configuration file '{}' in the path.".format(in_file))
        if clear_before_load:
            self.clear()
        self.config.read(in_file)

    @classmethod
    def clear(cls):
        cls.config.clear()

    @classmethod
    def get(cls, *items):
        c = cls.config
        for item in items:
            c = c[item]
        return c

    def __getitem__(cls, item):
        return cls.config[item]


def get_version_and_updated():
    info = Config()[Section.version]
    major = info.get("major")
    minor = info.get("minor")
    patch = info.get("patch")
    version_string = "{}.{}.{}".format(major, minor, patch)
    return version_string, Config.get(Section.version, Subsection.last_updated)


def sloppy_config_load():
    try:
        Config(r"C:\Users\admin\PycharmProjects\x\roll_one_for_me\config.ini")
    except FileNotFoundError:
        Config(r"/Users/prhomberg/personal_repos/roll_one_for_me/config.ini")

if __name__ == "__main__":
    sloppy_config_load()
    print(get_version_and_updated())
    pass
