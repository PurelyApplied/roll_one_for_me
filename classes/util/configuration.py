import configparser
from enum import Enum
from os import path


class Section(str, Enum):
    """Enum specifying required keys for config.ini"""
    version = "version"
    sentinel = "sentinel"
    sleep = "sleep"
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
    # sleep
    between_attempts = "between_attempts"
    between_checks = "between_checks"
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

    def __getitem__(self, item):
        return self.config[item]


def get_version_and_updated():
    info = Config()[Section.version]
    major = info.get("major")
    minor = info.get("minor")
    patch = info.get("patch")
    version_string = "{}.{}.{}".format(major, minor, patch)
    return version_string, Config.get(Section.version, Subsection.last_updated)


# noinspection SpellCheckingInspection
def sloppy_config_load():
    try:
        Config(r"C:\Users\admin\PycharmProjects\x\roll_one_for_me\config.ini")
    except FileNotFoundError:
        pass

    try:
        Config(r"/Users/prhomberg/personal_repos/roll_one_for_me/config.ini")
    except FileNotFoundError:
        pass

    Config(r"~/RofM/config.ini")


# noinspection PyTypeChecker
def config_is_complete_and_concise_test():
    sloppy_config_load()
    config_specified_sections = list(Config.config.keys())
    config_specified_subsections = [k for s in list(Config.config.values()) for k in s.keys()]

    # Ignore "DEFAULT" section in config
    default = {"DEFAULT"}
    config_specified_sections = set(config_specified_sections).difference(default)
    config_specified_subsections = set(config_specified_subsections).difference(default)

    enumerated_sections = set(s.name for s in Section).difference(default)
    enumerated_subsections = set(s.name for s in Subsection).difference(default)

    sections_missing_enum = config_specified_sections.difference(enumerated_sections)
    subsections_missing_enum = config_specified_subsections.difference(enumerated_subsections)

    sections_missing_config = enumerated_sections.difference(config_specified_sections)
    subsections_missing_config = enumerated_subsections.difference(config_specified_subsections)

    assert not sections_missing_config, "sections_missing_config: {}".format(sections_missing_config)
    assert not sections_missing_enum, "sections_missing_enum: {}".format(sections_missing_enum)
    assert not subsections_missing_config, "subsections_missing_config: {}".format(subsections_missing_config)
    assert not subsections_missing_enum, "subsections_missing_enum: {}".format(subsections_missing_enum)


if __name__ == "__main__":
    sloppy_config_load()
    print(get_version_and_updated())
    config_is_complete_and_concise_test()
    pass
