"""gcal-discord-poster auth subcommand."""

import argparse
import logging

import conf

COMMAND = "auth"

LOG = logging.getLogger("gcal-discord-poster")


# pylint: disable=protected-access
def register_parser(parser: argparse._SubParsersAction):
    """Constructs a subparser for the auth subcommand."""

    subparser = parser.add_parser(
        COMMAND,
        prog="gcal-discord-poster auth",
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
