#!/usr/bin/env python3

import datetime
import configparser
import os

from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
#import tzlocal

from utils import *

# delete token.json if modifying these scopes:
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.events"]
HERE = os.path.dirname(__file__) # current directory
#TIMEZONE = tzlocal.get_localzone().zone # IANA Time Zone Database name
TIMEZONE = "America/Los_Angeles"

def make_img_dir() -> str:
    """
    Checks for a tmp_images directory in the top level of the repository or creates it if it doesn't
    exist.

    Returns:
        The path to tmp_images
    """
    img_dir = f"{HERE}/tmp_images"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def printscreen():
    """
    Calls the screenshot program (as configured in config.ini) and saves the screenshot in
    tmp_images.
    """
    save_as = f"{make_img_dir()}/tmp.png"
    config_file = f"{HERE}/config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    command = f"{config['cli']['screenshotter']} {config['cli']['args']} {save_as}"
    os.system(command)

def authenticate() -> Resource:
    """
    Authenticates this client using the OAuth 2.0 client ID in a credentials.json file (should be
    located in the top level of the repository) and credentials obtained via launching the default
    browser and prompting for a login to the Google account to connect.

    Returns:
        A service object for interacting with that Google account's calendar
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
####################################################################################################

if __name__ == "__main__":
    # use RFC3339 date-time value:
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
    #service = authenticate()
    service = build("calendar", "v3", credentials=creds)
    service.events().insert(calendarId="primary", body={"summary": "foo","start": {"timeZone": TIMEZONE, "dateTime": "2021-05-07T01:15:34+00:00"}, "end": {"timeZone": TIMEZONE, "dateTime": "2021-05-08T01:15:34+00:00"}, })
