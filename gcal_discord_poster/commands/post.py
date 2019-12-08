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

"""gcal-discord-poster post subcommand."""

import argparse
import datetime
import logging

import gcal_discord_poster.commands as commands

import inflection

from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
from googleapiclient.discovery import build

import gcal_discord_poster.utils.conf as conf

COMMAND = "post"

YES_COMMANDS = {"y", "yes"}
NO_COMMANDS = {"n", "no"}
ABORT_COMMANDS = {"a", "abort"}

CHOICE_YES = 0
CHOICE_NO = 1
CHOICE_ABORT = 2
CHOICE_RETRY = 3

LOG = logging.getLogger("gcal-discord-poster")


def post_discord_webhook(url: str, event: dict, attributes: dict):
    """Post Discord webhook using a Google calendar event and attributes.

    :param url: webhook url to post the Discord webhook body to.
    :param event: raw response from Google containing event information.
    :param attributes: data extracted from the event to store rich event info.
    """

    webhook = DiscordWebhook(url=url)
    embed = DiscordEmbed(
        title=event["summary"].strip(),
        description=attributes["description"],
        color=14329120)
    embed.set_author(
        name=attributes["location"],
        icon_url=attributes["author_image"])
    embed.set_thumbnail(url=attributes["thumbnail"])

    lead_count = len(attributes["leads"].split(","))
    lead_field_name = "Lead" if lead_count <= 1 else "Leads"
    event_start_time = google_parse_datetime(event["start"]["dateTime"])

    # Custom embed fields that we use.
    embed.add_embed_field(
        name=lead_field_name,
        value=attributes["leads"],
        inline=False)
    embed.add_embed_field(
        name="Date",
        value=humanize_datetime_date(event_start_time),
        inline=True)
    embed.add_embed_field(
        name="Time",
        value=humanize_datetime_time(event_start_time),
        inline=True)
    embed.add_embed_field(
        name="Req. Signup?",
        value=attributes["signup_required"],
        inline=True)

    # Signup sheet is 100% optional. I might push for using reactions to signup
    # as that's a bit easier, but keep this just in-case that doesn't work out.
    if "signup_sheet" in attributes:
        embed.add_embed_field(
            name="Signup Sheet",
            value=f"[Click Here]({attributes['signup_sheet']})",
            inline=True)
        embed.set_url(attributes["signup_sheet"])

    embed.add_embed_field(
        name="Req. Addons",
        value=attributes["addons"],
        inline=True)
    embed.add_embed_field(
        name="Req. ilvl / Min. DPS",
        value=attributes["requirements"],
        inline=True)

    embed.set_footer(
        text=attributes["submitter"],
        icon_url=attributes["footer_image"])

    webhook.add_embed(embed)

    return webhook.execute()


def interactive_confirm_event(event: dict) -> int:
    """Interactively asks the user through stdin to confirm an event post."""

    event_start_time = google_parse_datetime(event["start"]["dateTime"])
    human_start_time = humanize_datetime(event_start_time)

    answer = input(f"Post {event['summary']} @ {human_start_time}? [Y/n/a] ")

    if answer.lower() in YES_COMMANDS:
        return CHOICE_YES
    elif answer.lower() in NO_COMMANDS:
        return CHOICE_NO
    elif answer.lower() in ABORT_COMMANDS:
        return CHOICE_ABORT
    else:
        return CHOICE_RETRY


def get_adhoc_event_attributes(event: dict) -> dict:
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
                key = inflection.underscore(parts[0].strip())
                value = parts[1].strip()
                attributes[key] = value
            else:
                reading_attributes = False
        else:
            description += "\n" + line

    attributes["description"] = description.strip()

    return attributes


def humanize_datetime_date(dt: datetime.datetime) -> str:
    """Formats a datetime into a human-readable date."""

    return dt.strftime(f"%A, %B %-d{inflection.ordinal(dt.day)}")


def humanize_datetime_time(dt: datetime.datetime) -> str:
    """Formats a datetime into a human-readable time."""

    return dt.strftime("%-I:%M %p")


def humanize_datetime(dt: datetime.datetime) -> str:
    """Formats a datetime into a human-readable datetime."""

    return f"{humanize_datetime_date(dt)} {humanize_datetime_time(dt)}"


def google_isoformat(dt: datetime.datetime) -> str:
    """Returns a datetime in UTC isoformat, just as Google prefers."""

    return dt.isoformat() + "Z"


def google_parse_datetime(dt: str) -> datetime.datetime:
    """Parses a string datetime returned from the Google Calendar API."""

    return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%z")


def register_parser(config: dict, parser):
    """Constructs a subparser for the post subcommand."""

    subparser = parser.add_parser(
        COMMAND,
        prog="gcal_discord_poster.py post",
        description="Posts google calendar events to Discord.")
    subparser.add_argument(
        "-c", "--calendar", dest="calendar",
        help="The calendar id of the calendar to search for events on.")
    subparser.add_argument(
        "-w", "--webhook-url", dest="webhook_url",
        help="The url of the Discord webhook where we post to.")
    subparser.add_argument(
        "-d", "--days", dest="days", type=int, default=7,
        help="The maximum number of days to seek for events to post.")
    subparser.add_argument(
        "-s", "--skip-days", dest="skip_days", type=int, default=0,
        help="The number of days to skip when seeking for events to post.")

    return subparser


def run(config: dict, args: argparse.Namespace):
    """Runs the post command with the provided arguments."""

    calendar = args.calendar
    webhook_url = args.webhook_url
    days = int(args.days)
    skip_days = int(args.skip_days)

    if days < 0:
        LOG.error("Please specify a positive number of days.")
        return commands.EXIT_GENERIC_ERROR
    if skip_days >= days:
        LOG.error("Skip days must be less than seek days.")
        return commands.EXIT_GENERIC_ERROR

    # Use the calendar value from the config if not specified in the args.
    if not calendar:
        calendar = config.get("calendar")
        if not calendar:
            LOG.error("No calendar passed.")
            return commands.EXIT_GENERIC_ERROR

    # Use the webhook value from the config if not specified in the args.
    if not webhook_url:
        webhook_url = config.get("webhook_url")
        if not webhook_url:
            LOG.error("No webhook url passed.")
            return commands.EXIT_GENERIC_ERROR

    # Stash the argument values in the config to save to the filesystem later.
    config["calendar"] = calendar
    config["webhook_url"] = webhook_url

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
        calendarId=calendar,
        timeMin=google_isoformat(now + datetime.timedelta(days=skip_days)),
        timeMax=google_isoformat(now + datetime.timedelta(days=days)),
        maxResults=50,
        singleEvents=True,
        orderBy="startTime")
    events = events_query.execute()

    approved_events = []
    event_items = events.get("items", [])
    current_event = 0

    # Ask the user which events they want to post interactively. This input
    # flow works the same to the typical [Y/n] flow seen in many interactive
    # CLI programs.
    while current_event < len(event_items):
        event = event_items[current_event]
        choice = interactive_confirm_event(event)

        if choice == CHOICE_YES:
            approved_events.append(event)
            current_event += 1
        elif choice == CHOICE_NO:
            current_event += 1
        elif choice == CHOICE_ABORT:
            LOG.info("Aborting posting to Discord, quitting...")
            return commands.EXIT_SUCCESS

    if len(approved_events) > 0:
        LOG.info("Posting %d events to %s", len(approved_events), webhook_url)

        # Iterate over only approved posts and post them to the webhook.
        for event in approved_events:
            attributes = get_adhoc_event_attributes(event)
            post_discord_webhook(webhook_url, event, attributes)

        LOG.info("Webhook publishes completed successfully!")
    else:
        LOG.info("No events to publish to Discord, quitting...")

    conf.save_config(config)

    return commands.EXIT_SUCCESS
