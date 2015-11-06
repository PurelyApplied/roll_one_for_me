from os import path
import configparser
import semver


class Section:
    """Enum specifying permissible keys for config.ini"""
    version = "version"
    sentinel = "sentinel"
    sleep = "sleep"
    logging = "logging"
    dice = "dice"
    links = "links"


class Config:
    """Singleton container wrapping configparser calls."""
    config = configparser.ConfigParser()

    def __init__(self, in_file=None):
        if in_file:
            self.load(in_file)

    @classmethod
    def load(cls, in_file="config.ini", clear_before_load=True):
        if not path.exists(in_file):
            raise FileNotFoundError("Cannot find configuration file '{}' in the path.".format(in_file))
        if clear_before_load:
            cls.clear()
        cls.config.read(in_file)

    @classmethod
    def clear(cls):
        cls.config.clear()

    @classmethod
    def __getitem__(cls, item):
        return cls.config[item]


def get_version_string():
    info = Config()[Section.version]
    major = info.get("major")
    minor = info.get("minor")
    patch = info.get("patch")
    return "{}.{}.{}".format(major, minor, patch)


if __name__ == "__main__":
    Config(r"C:\Users\admin\PycharmProjects\x\roll_one_for_me\config.ini")
    print(get_version_string())
    pass
