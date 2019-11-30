#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2019 Walter Kuppens
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Start point for gcal-discord-poster."""

import argparse
import logging
import os
import sys

import commands.auth as auth
import commands.post as post
import utils.conf as conf

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
CLIENT_ID_PATH = os.path.join(DIR_PATH, "client_id.json")

LOG = logging.getLogger("gcal-discord-poster")


def get_parser(config: dict):
    """Returns the top-level parser for gcal-discord-poster."""

    parser = argparse.ArgumentParser(
        prog="gcal_discord_poster.py",
        description="Translates upcoming calendar events into Discord embeds "
                    "and posts them to a webhook url.")
    parser.add_argument(
        "--client-id-file", dest="client_id_file", default=CLIENT_ID_PATH,
        help="File path to the client id file for the OAUTH2 flow. If left "
             "unspecified then the file is read from the same directory the "
             "script is installed to.")

    subparsers = parser.add_subparsers(help="commands", dest="command")
    auth.register_parser(config, subparsers)
    post.register_parser(config, subparsers)

    return parser


def main():
    """Program start point."""

    handler = logging.StreamHandler(sys.stdout)
    LOG.addHandler(handler)
    LOG.setLevel(logging.INFO)

    app_config = conf.get_config()

    parser = get_parser(app_config)
    args = parser.parse_args()

    if args.command == auth.COMMAND:
        sys.exit(auth.run(app_config, args))
    if args.command == post.COMMAND:
        sys.exit(post.run(app_config, args))

    parser.print_usage()


if __name__ == "__main__":
    main()
