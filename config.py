#!/usr/bin/env python3

import fileinput
import re
from typing import Dict

def get_old_settings() -> Dict[str, str]:
    """Read config.ini to extract current settings.

    Returns:
        Dictionary of configuration options and their current values.
    """
    old_settings = {} # old settings and their corresponding values
    with open("config.ini", "r") as file:
        # Read each line to extract current settings:
        for line in file.readlines():
            # Ignore headers and comments:
            if line[0] == "[" or line[0] == ";":
                continue
            else:
                # Read current settings and their values:
                key, value = re.split("=", line, 1)
                old_settings[key] = value
    return old_settings
    
def get_new_settings() -> Dict[str, str]:
    """Ask the user for new settings.

    Returns:
        Dictionary of configuration options and their desired values.
    """
    new_settings = {} # new settings and their corresponding values
    # Get name of screenshot cli program:
    print("\nWhat is the command to call your screenshot program?")
    inp = input("Press enter for the default selection: xfce4-screenshooter\n")
    if not inp == "":
        new_settings["screenshotter"] = inp + "\n"
        print()
    else:
        new_settings["screenshotter"] = "xfce4-screenshooter\n"
    # Get arguments to make it shoot and save a selected region of the screen:
    print("What arguments does it require to take and save a screenshot of a selected region?")
    inp = input("Press enter for the default selection: -rs\n")
    if not inp == "":
        new_settings["args"] = inp + "\n"
        print()
    else:
        new_settings["args"] = "-rs\n"
    # Get calendar ID:
    print("What is the ID of the Google calendar you would like to add your shifts to?")
    inp = input("Press enter for the default selection: primary\n")
    if not inp == "":
        new_settings["calendar"] = inp + "\n"
        print()
    else:
        new_settings["calendar"] = "primary\n"
    return new_settings

if __name__ == "__main__":
    # Read current ini settings and prompt user for new ones:
    old_settings = get_old_settings()
    new_settings = get_new_settings()
    # Write updated settings to config.ini:
    with fileinput.input("config.ini", inplace=True) as file:
        for line in file:
            if line[0] == "[" or line[0] == ";":
                print(line, end="")
            else:
                key, value = re.split("=", line, 1)
                old_text = f"{key}={old_settings[key]}"
                new_text = f"{key}={new_settings[key]}"
                print(line.replace(old_text, new_text), end="")
