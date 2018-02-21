#!/usr/bin/env python3

import argparse

from rofm.legacy.legacy_main import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str,
                        help="Path to config.ini",
                        default="config.ini")
    parser.add_argument("--long-lived", dest="long_lived", action='store_true',
                        help="Without this flag, log in and process exactly one pass.")

    args = parser.parse_args()
    main(args.long_lived, args.config)
