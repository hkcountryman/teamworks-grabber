#!/bin/bash

# Bind this script to a key that can be pressed while Teamworks is open.
# This means the script needs execute and read permissions (chmod u+r+x).
# XFCE Settings Manager > Keyboard > Application Shortcuts
# I mapped mine (~/GitHub/capture_window.sh) to super + print.

# Check for directory to temporarily store screenshots:
if [ ! -d "/home/halle/GitHub/teamworks-grabber/tmp_images" ]
then
    # Create it if absent:
    mkdir /home/halle/GitHub/teamworks-grabber/tmp_images
fi

# Take a picture of the active window and save it in the temp folder:
xfce4-screenshooter -rs ~/GitHub/teamworks-grabber/tmp_images/tmp.png
