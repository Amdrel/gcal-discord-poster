"""gcal-discord-poster post subcommand."""

import argparse
import datetime
import logging

import commands

from bs4 import BeautifulSoup
from googleapiclient.discovery import build

import conf


COMMAND = "post"

LOG = logging.getLogger("gcal-discord-poster")


def get_adhoc_event_attributes(event):
    """Parses human-written custom event attributes into a dictionary.

    Although Google Calendar support custom attributes, they aren't editable
    from the user-facing interface. To make re-configuration of events
    easier, I made it so custom attributes can be specified in the event
    description.
    """

    raw_description = event.get("description", "")
    raw_description = raw_description.replace("<br>", "\n")

    content = BeautifulSoup(raw_description, features="html.parser")
    text_description = content.get_text()

    attributes = {}
    description = ""
    reading_attributes = True

    for line in text_description.splitlines():
        if reading_attributes:
            parts = line.split(":", 1)
            if len(parts) == 2:
                attributes[parts[0].strip()] = parts[1].strip()
            else:
                reading_attributes = False
        else:
            description += "\n" + line

    attributes["description"] = description.strip()

    return attributes


def google_isoformat(dt: datetime.datetime) -> str:
    """Returns a datetime in UTC isoformat, just as Google prefers."""

    return dt.isoformat() + "Z"


def register_parser(parser):
    """Constructs a subparser for the post subcommand."""

    subparser = parser.add_parser(
        COMMAND,
        prog="gcal-discord-poster post",
        description="Posts google calendar events to Discord.")
    subparser.add_argument(
        "-c", "--calendar", dest="calendar", required=True,
        help="The calendar id of the calendar to search for events on.")
    subparser.add_argument(
        "-d", "--days", dest="days", type=int, default=7,
        help="The maximum number of days to seek for events to post.")

    return subparser


def run(config: dict, args: argparse.Namespace):
    """Runs the post command with the provided arguments."""

    if args.days < 0:
        LOG.error("Please specify a positive number of days.")
        return commands.EXIT_GENERIC_ERROR

    credentials = conf.get_saved_google_credentials(config)
    if not credentials:
        LOG.error(
            "Cannot read calendar as the CLI is not authenticated, aborting. "
            "Please run the 'auth' subcommand to authenticate the CLI.")
        return commands.EXIT_GENERIC_ERROR

    service = build("calendar", "v3", credentials=credentials)
    events_service = service.events()  # pylint: disable=no-member

    now = datetime.datetime.utcnow()

    events_query = events_service.list(
        calendarId=args.calendar,
        timeMin=google_isoformat(now),
        timeMax=google_isoformat(now + datetime.timedelta(days=args.days)),
        maxResults=50,
        singleEvents=True,
        orderBy="startTime")
    events = events_query.execute()

    for event in events.get("items", []):
        # start = event["start"].get("dateTime", event["start"].get("date"))

        attributes = get_adhoc_event_attributes(event)

        # import json
        # print(json.dumps(event, indent=2, sort_keys=True))
        # print(start, event["summary"])

    return commands.EXIT_SUCCESS
