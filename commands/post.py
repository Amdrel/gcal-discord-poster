"""gcal-discord-poster post subcommand."""

import logging

COMMAND = "post"

LOG = logging.getLogger("gcal-discord-poster")


def register_parser(parser):
    """Constructs a subparser for the post subcommand."""

    subparser = parser.add_parser(
        COMMAND,
        prog="gcal-discord-poster post",
        description="Posts google calendar events to Discord.")

    return subparser


def run(config, args):
    """Runs the post command with the provided arguments."""

    pass
