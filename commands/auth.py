"""gcal-discord-poster auth subcommand."""

import logging

COMMAND = "auth"

# Google API scopes required for the operation of this tool.
SCOPES = {
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events.readonly",
}

LOG = logging.getLogger("gcal-discord-poster")


def register_parser(parser):
    """Constructs a subparser for the auth subcommand."""

    subparser = parser.add_parser(
        COMMAND,
        prog="gcal-discord-poster auth",
        description="Authenticates with Google so the program can get access "
                    "to the user's calendar.")

    return subparser


def run(config, args):
    """Runs the auth command with the provided arguments."""

    pass
