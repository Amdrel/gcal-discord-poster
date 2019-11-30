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

"""gcal-discord-poster auth subcommand."""

import argparse
import logging

import commands
import utils.conf as conf

COMMAND = "auth"

LOG = logging.getLogger("gcal-discord-poster")


def register_parser(config: dict, parser):
    """Constructs a subparser for the auth subcommand."""

    subparser = parser.add_parser(
        COMMAND,
        prog="gcal_discord_poster.py auth",
        description="Authenticates with Google so the program can get access "
                    "to the user's calendar.")

    return subparser


def run(config: dict, args: argparse.Namespace):
    """Runs the auth command with the provided arguments."""

    credentials = conf.get_saved_google_credentials(config)
    if not credentials:
        LOG.info("CLI is not authenticated, starting OAuth2 flow.")
        conf.get_new_google_credentials(config, args.client_id_file)
    else:
        LOG.info("CLI is already authenticated.")

    return commands.EXIT_SUCCESS
