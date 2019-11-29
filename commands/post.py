"""gcal-discord-poster post subcommand."""

import argparse
import logging

COMMAND = "post"

LOG = logging.getLogger("gcal-discord-poster")


# pylint: disable=protected-access
def register_parser(parser: argparse._SubParsersAction):
    """Constructs a subparser for the post subcommand."""

    subparser = parser.add_parser(
        COMMAND,
        prog="gcal-discord-poster post",
        description="Posts google calendar events to Discord.")

    return subparser


def run(config: dict, args: argparse.Namespace):
    """Runs the post command with the provided arguments."""
