#!/usr/bin/env python3

from datetime import date, datetime, time, timedelta
import configparser
import os
from pathlib import Path
from typing import Union
from utils.LocalTimezone import LocalTimezone

from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from utils.AskDate import AskDate
from utils import shifts_to_text
from utils.shifts_to_text import DAYS_IN_WEEK

####################################################################################################

# Delete token.json if modifying these scopes:
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events"
    ]
HERE = os.path.dirname(__file__) # directory containing this program
IMAGEDIR = "tmp_images/" # directory containing screenshots (inside HERE)
SCHEDULE = "tmp.png" # schedule picture (inside IMAGEDIR)
TIMEZONE: str # IANA time zone name
MONDAY: date # first day of the week

def make_img_dir() -> str:
    """Checks for a tmp_images directory in the top level of the repository or creates it if it
    doesn't exist.

    Returns:
        The path to tmp_images.
    """
    img_dir = f"{HERE}/tmp_images"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def printscreen() -> str:
    """Calls the screenshot program (as configured in config.ini) and saves the screenshot in the
    tmp_images directory.
    """
    save_as = f"{make_img_dir()}/tmp.png"
    config_file = f"{HERE}/config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    command = f"{config['cli']['screenshotter']} {config['cli']['args']} {save_as}"
    os.system(command)

def authenticate() -> Resource:
    """Authenticates this client using the OAuth 2.0 client ID in a credentials.json file (should be
    located in the top level of the repository) and credentials obtained via launching the default
    browser and prompting for a login to the Google account to connect.

    Returns:
        A service object for interacting with that Google account's calendar.
    """
    creds = None
    # token.json stores the user's access and refresh tokens, and is created automatically when the
    # authorization flow completes for the first time:
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in:
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json()) # save the credentials for the next run
    return build("calendar", "v3", credentials=creds)

def which_week() -> date:
    """Asks the user which week they are uploading to the calendar and determines Monday's date that
    week.

    Returns:
        The Monday of the week to be uploaded.
    """
    # Get possible Mondays (this week, next week, or the week after):
    today = date.today()
    monday1 = today - timedelta(days=today.weekday()) # last monday
    monday2 = monday1 + timedelta(days=7) # next monday
    monday3 = monday2 + timedelta(days=7) # next next monday
    # Get the actual Monday from the schedule:
    schedule_monday = AskDate().response.get() # first date on schedule
    if schedule_monday == "This week":
        return monday1
    elif schedule_monday == "Next week":
        return monday2
    else: # two weeks out
        return monday3

def get_events(file: Union[Path, str]) -> list:
    """Obtains a list of the events to add to the calendar for the week shown in the schedule.

    Args:
        file: A PNG depicting the week's schedule.

    Returns:
        A list of JSON serializables describing events to add to the calendar.
    """
    shifts = shifts_to_text.shifts(file)
    # Add JSON serializable events to list:
    events = []
    for i in range(DAYS_IN_WEEK):
        day = MONDAY + timedelta(days=i) # shift date
        start_time, end_time = shifts[i] # shift start and end time
        if start_time != None:
            local = LocalTimezone() # use to get offset from UTC
            start_datetime = datetime.combine(day, start_time, tzinfo=local) # shift start datetime
            end_datetime = datetime.combine(day, end_time, tzinfo=local) # shift end datetime
            events.append({
                "summary": "Starbucks",
                "start"  : {"timeZone": TIMEZONE, "dateTime": f"{start_datetime.isoformat()}"},
                "end"    : {"timeZone": TIMEZONE, "dateTime": f"{end_datetime.isoformat()}"}
            })
    return events

if __name__ == "__main__":
    # Authenticate to read and write to the calendar:
    service = authenticate()
    # Which calendar are we using?
    config_file = f"{HERE}/config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    calendarId = f"{config['calendar_api']['calendar']}"
    # Request IANA time zone of calendar:
    TIMEZONE = service.calendarList().get(calendarId=calendarId).execute()["timeZone"]
    # Take screenshot of schedule, including only scheduled (not punched) hours and days:
    printscreen()
    # Determine bounds of week we are editing:
    MONDAY = which_week()
    # Retrieve list of events scheduled in that week:
    events_search = service.events().list( # events already in this week
        calendarId=calendarId,
        timeMin=(datetime.combine( # creating a datetime based on MONDAY
            date=MONDAY,
            time=time(hour=0, minute=0),
            tzinfo=LocalTimezone())
            ).isoformat()
        ).execute()
    existing_events = events_search.get("items", [])
    # If the shift is not already scheduled, add it:
    for event in get_events(f"{IMAGEDIR}{SCHEDULE}"):
        if event not in [{ # summary of existing events to only include summary, start, and end
            "summary": x["summary"],
            "start"  : x["start"],
            "end"    : x["end"]
            } for x in existing_events]:
            service.events().insert(calendarId=calendarId, body=event).execute()
