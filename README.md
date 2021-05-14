# teamworks-grabber
Use a command line program that can grab screenshots of portions of your screen to snap a picture of the Teamworks website, read the image with Tesseract OCR, and upload your shifts to your Google calendar. If it sounds like overkill to you, you underestimate how much I object to using a separate calendar for my work schedule. Also I was scared to get banned if I tried scraping the HTML.

## Requirements
- Python 3.6+
- Probably Linux, unless you know of a command line screenshot program for other systems
- Tesseract, which can probably be installed through your package manager
- An account with [Google Cloud Platform](https://console.cloud.google.com/getting-started). See [the wiki](https://github.com/hkcountryman/teamworks-grabber/wiki#integrating-auth-into-the-program) for further instructions.

## Usage
Prior to use, be sure to ```pip install -r requirements.txt``` and run the config.py script to set up config.ini, or just edit it manually. As you can see in the [default config.ini](https://github.com/hkcountryman/teamworks-grabber/blob/main/config.ini), it stores the name of the screenshot program (gnome-screenshot, but it could be any command line screenshot program you like), the arguments passed to that program to make it take a screenshot of a selected region and save the image (-af, in the case of gnome-screenshot), and the Google Calendar ID of the calendar in which the shifts will be added (primary, or an ID found in calendar settings under "Integrate Calendar"). That's because I want my shifts added to my primary calendar and because the command to capture and save a portion of the screen using gnome-screenshot is:
```
$ gnome-screenshot -af [path to image]/[image name].[file extension]
```
The image file path should not be included in config.ini!

When you run teamworks.py, it makes a call to [os.system()](https://docs.python.org/3/library/os.html#os.system) to run a command much like the above and you will be immediately prompted to take a screenshot, which should include the scheduled shifts and their dates for one week (see [the example of a valid screenshot](https://github.com/hkcountryman/teamworks-grabber/wiki#example-of-a-valid-screenshot)). As such, I recommend setting up a keybind to run teamworks.py so you can log into Teamworks and take the screenshot from there. You may have to edit read/write permissions of the script in order to use it with a keybind.

Be advised, the program can only add shifts that are scheduled for the current week or the next two weeks after.

## "Mostly functional"
Currently it doesn't work for weeks with shifts that are multiple coverage types, for example if you train for the first half of your shift and provide floor coverage for the second half. I'm getting to that.
