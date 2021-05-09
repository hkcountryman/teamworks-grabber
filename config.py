#!/usr/bin/env python3

import re

if __name__ == "__main__":
    new_settings = {} # new settings and their corresponding values
    # Get name of screenshot cli program:
    print("What is the command to call your screenshot program?\nPress enter for the default selection: xfce4-screenshooter")
    inp = input()
    new_settings["screenshotter"] = inp if not inp == "" else "xfce4-screenshooter"
    # Get arguments to make it shoot and save a selected region of the screen:
    print("What arguments does it require to take and save a screenshot of a selected region? (Do not include the file path!)\nPress enter for the default selection: -rs")
    inp = input()
    new_settings["args"] = inp if not inp == "" else "-rs"
    # Get calendar ID:
    print("What is the ID of the Google calendar you would like to add your shifts to?\nPress enter for the default selection: primary")
    inp = input()
    new_settings["calendar"] = inp if not inp == "" else "primary"
    # Edit config.ini with obtained values:
    with open("config.ini", "a+") as f:
        for line in f.readlines():
            # Ignore headers and comments:
            if line[0] == "[" or line[0] == ";":
                continue
            else:
                # Read current settings and their values:
                #key, value = re.split("=", line, 1)
                # Replace with value from new settings:
                #str.replace(line.strip(), f"{key}={new_settings[key]}\n")
