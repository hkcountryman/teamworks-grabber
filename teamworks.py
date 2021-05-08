#!/usr/bin/env python3

from datetime import date, timedelta
import configparser
import os
from pathlib import Path
from typing import Union

from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from utils import shifts_to_text
from utils.shifts_to_text import DAYS_IN_WEEK

# delete token.json if modifying these scopes:
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events"
    ]
HERE = os.path.dirname(__file__) # directory containing this file
global TIMEZONE # IANA time zone name

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

def printscreen():
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
    # if there are no (valid) credentials available, let the user log in:
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json()) # save the credentials for the next run
    return build("calendar", "v3", credentials=creds)

def which_week(file: Union[Path, str]) -> date:
    """Extrapolates which week is to be filled out based on the number of the first day of the week
    depicted in the schedule. We assume that today's date is within or before the week being
    uploaded. Because Starbucks schedules are written three weeks out, there are only three possible
    Mondays that might be depicted. Whichever has a date matching the number read from the schedule
    must be in the week to be filled out.

    Args:
        file: A PNG depicting the week's schedule.

    Returns:
        The Monday of the week to be filled out.

    Raises:
        RuntimeError: If no Mondays in the next three week match.
    """
    schedule_monday = shifts_to_text.date(file) # first date on schedule
    today = date.today()
    monday1 = today - timedelta(days=today.weekday()) # last monday
    monday2 = monday1 + timedelta(days=7) # next monday
    monday3 = monday2 + timedelta(days=7) # next next monday
    date_objs = [monday1, monday2, monday3] # list of possible mondays as datetime.date objects
    if schedule_monday in (date_strs := [day.strftime("%d") for day in date_objs]):
        return date_objs[date_strs.index(schedule_monday)]
    else:
        raise RuntimeError("No Monday with that date occurs in the next three weeks.")

def get_event_times(file: Union[Path, str]):
    shifts = shifts_to_text.shifts(file)
    monday = which_week(file) # first day of the week
    for i in range(DAYS_IN_WEEK):
        day = monday + timedelta(days=i)
        if shifts[i] != None:
            print(shifts[i])
####################################################################################################

if __name__ == "__main__":
    creds = None
    # token.json stores the user's access and refresh tokens, and is created automatically when the
    # authorization flow completes for the first time:
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # if there are no (valid) credentials available, let the user log in:
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json()) # save the credentials for the next run
    service = authenticate()
    # request IANA time zone of primary calendar:
    TIMEZONE = service.calendarList().get(calendarId="primary").execute()["timeZone"]
    get_event_times("tmp_images/tmp.png")
    '''event = {
        "summary": "foo",
        "start": {"timeZone": TIMEZONE, "dateTime": "2021-05-07T01:15:34+00:00"},
        "end": {"timeZone": TIMEZONE, "dateTime": "2021-05-08T01:15:34+00:00"}
        }
    service.events().insert(calendarId="primary", body=event).execute()'''