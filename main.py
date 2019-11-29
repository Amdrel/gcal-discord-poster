#!/usr/bin/env python3

"""Start point for gcal-discord-poster."""

import argparse
import logging
import os
import sys

import commands.auth as auth
import commands.post as post
import conf

LOG = logging.getLogger("gcal-discord-poster")


def get_parser():
    """Returns the top-level parser for gcal-discord-poster."""

    parser = argparse.ArgumentParser(
        prog="gcal-discord-poster",
        description="Translates upcoming calendar events into Discord embeds "
                    "and posts them to a webhook url.")

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

    dir_path = os.path.dirname(os.path.realpath(__file__))
    client_id_path = os.path.join(dir_path, "client_id.json")
    if not os.path.isfile(client_id_path):
        raise RuntimeError("No client id file is present, cannot continue.")

    if args.command == auth.COMMAND:
        auth.run(app_config, args)
    elif args.command == post.COMMAND:
        post.run(app_config, args)
    else:
        parser.print_usage()


if __name__ == "__main__":
    main()
