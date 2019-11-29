#!/usr/bin/env python3

"""Start point for gcal-discord-poster."""

import argparse
import logging
import os
import sys

import commands.auth as auth
import commands.post as post
import conf

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
CLIENT_ID_PATH = os.path.join(DIR_PATH, "client_id.json")

LOG = logging.getLogger("gcal-discord-poster")


def get_parser():
    """Returns the top-level parser for gcal-discord-poster."""

    parser = argparse.ArgumentParser(
        prog="gcal-discord-poster",
        description="Translates upcoming calendar events into Discord embeds "
                    "and posts them to a webhook url.")
    parser.add_argument(
        "--client-id-file", dest="client_id_file", default=CLIENT_ID_PATH,
        help="File path to the client id file for the OAUTH2 flow. If left "
             "unspecified then the file is read from the same directory the "
             "script is installed to.")

    subparsers = parser.add_subparsers(help="commands", dest="command")
    auth.register_parser(subparsers)
    post.register_parser(subparsers)

    return parser


def main():
    """Program start point."""

    handler = logging.StreamHandler(sys.stdout)
    LOG.addHandler(handler)
    LOG.setLevel(logging.DEBUG)

    parser = get_parser()
    args = parser.parse_args()

    app_config = conf.get_config()

    if args.command == auth.COMMAND:
        auth.run(app_config, args)
    elif args.command == post.COMMAND:
        post.run(app_config, args)
    else:
        parser.print_usage()


if __name__ == "__main__":
    main()
