"""Default config values, as well as config handling."""

import configparser


def get_default_config(**kwargs):
    """ This example pulled from the docs."""
    config = configparser.ConfigParser(**kwargs)
    config['DEFAULT'] = {'ServerAliveInterval': '45',
                         'Compression': 'yes',
                         'CompressionLevel': '9'}
    config['bitbucket.org'] = {}
    config['bitbucket.org']['User'] = 'hg'
    config['topsecret.server.com'] = {}
    topsecret = config['topsecret.server.com']
    topsecret['Port'] = '50022'     # mutates the parser
    topsecret['ForwardX11'] = 'no'  # same here
    config['DEFAULT']['ForwardX11'] = 'yes'

    config['sleep']={}
    config['sleep']['between_passes'] = "15 # seconds"
    return config


def write_config_file():
    with open('example.ini', 'w') as configfile:
        config = get_default_config()
        config.write(configfile)
