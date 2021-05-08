from dataclasses import astuple
from datetime import datetime, time
import re
from typing import List, Tuple, Union
from pathlib import Path

from PIL import Image, ImageOps
from pytesseract import image_to_string

from .CropBox import CropBox

####################################################################################################

DAYS_IN_WEEK = 7
BRIGHT_GREEN = (0, 128, 0) # RGB value for the green on the schedule

def date(file: Union[Path, str]) -> str:
    """Get the number of the first day of the week (Monday).

    Args:
        file: A PNG depicting the week's schedule.

    Returns:
        The number of the day (2 digits) as a string.
    """
    img = Image.open(file)
    width, height = img.size
    # Extract portion of calendar with Monday:
    boundaries = CropBox(left=0, top=0, right=width//7, bottom=height//3) # boundaries to crop
    monday = img.crop(astuple(boundaries))
    # Read number from Monday:
    date = image_to_string(monday)
    number = int("".join(filter(str.isdigit, date)))
    return f"0{number}" if number < 10 else str(number)

def shifts(file: Union[Path, str]) -> List[Tuple[Union[time, None]]]:
    """Read and return a list of the text from each shift in a week.

    Args:
        file: A PNG depicting the week's schedule.

    Returns:
        A list of shifts as tupples with start and end times (or None for no shift), starting with
        Monday's shift.
    """
    divide_days(file)
    shifts = [get_shift(f"tmp_images/tmp{x}.png") for x in range(DAYS_IN_WEEK)] # shifts as strings
    return [shift_to_tuple(x) for x in shifts]

'''def shifts_old(file: Union[Path, str]) -> List[Union[str, None]]:
    """Read and return a list of the text from each shift in a week.

    Args:
        file: A PNG depicting the week's schedule.

    Returns:
        A list of shifts as strings (or None for no shift), starting with Monday's shift.
    """
    divide_days(file)
    return [get_shift(f"tmp_images/tmp{x}.png") for x in range(7)]'''

def divide_days(file: Union[Path, str]):
    """Given an image of the schedule for a whole week, saves 7 images in the tmp_images directory,
    1 for each separate day and labeled tmp0.png - tmp6.png, starting with Monday.

    Args:
        file: The PNG depicting the week's schedule.
    """
    img = Image.open(file)
    width, height = img.size
    crop_width = width // DAYS_IN_WEEK # width of image of one day
    boundaries = CropBox(left=0, top=0, right=0, bottom=height-1) # boundaries to crop
    for i in range(DAYS_IN_WEEK):
        filename = f"tmp_images/tmp{i}.png"
        boundaries.left = crop_width * i
        boundaries.right = crop_width * (i + 1) - 1
        img.crop(astuple(boundaries)).save(filename)

def extract_content(file: Union[Path, str]) -> Image:
    """Given an image of the schedule for a single day, crops the image to only contain the lower
    portion so that it shows the scheduled shift but not the date. If the scheduled shift appears
    against a green background, the image is then inverted to make it easier for the OCR to read.

    Args:
        file: The PNG depicting the day's schedule.

    Returns:
        The cropped (and possibly inverted) PIL.Image object.
    """
    img = Image.open(file)
    width, height = img.size
    border = height // 3 # border where lower section starts
    boundaries = CropBox(left=0, top=border, right=width-1, bottom=height-1) # boundaries to crop
    lower_section = img.crop(astuple(boundaries))
    # Check if the image is white text on a green background:
    center = tuple(pixel // 2 for pixel in lower_section.size)
    center_pixel = lower_section.getpixel(center)
    # Tesseract has problems reading white text on green; may need to invert:
    return ImageOps.invert(lower_section) if center_pixel == BRIGHT_GREEN else lower_section

def get_shift(file: Union[Path, str]) -> Union[str, None]:
    """Given an image of the schedule for a single day, read the scheduled shift from the image.

    Args:
        file: The PNG depicting the day's schedule.

    Returns:
        A string with the start and end times of the scheduled shift, or None on a day off.
    """
    shift = image_to_string(extract_content(file)).split("\n")[0] # my shift
    # Occasionally Tesseract mistakenly sees the following characters at the beginning or end of the
    # shift strings:
    if shift[0] == "(" or shift[0] == "{":
        shift = shift[1:]
    if shift[-1] == ".":
        shift = shift[:-1]
    return None if shift == "\x0c" else shift # \x0c is a whitespace constant for days with no shift

def shift_to_tuple(shift: Union[str, None]) -> Tuple[Union[time, None]]:
    """Given a shift as a string, parses it to time objects and returns the start and end times.

    Args:
        shift: The shift string, for example "04:30 pm - 09:00 pm".

    Returns:
        A tuple containing the start time and end time objects, or (None, None) for no shift.
    """
    if shift == None:
        return (None, None)
    else:
        start, end = re.split("-", shift, 1)
        # Extract from the strings (%I:%M %p corresponds to hour:minute AM/PM):
        start_datetime = datetime.strptime(start.strip(), "%I:%M %p")
        end_datetime = datetime.strptime(end.strip(), "%I:%M %p")
        # Convert from datetimes to times (independent of a particular day):
        start_time = time(hour=start_datetime.hour, minute=start_datetime.minute)
        end_time = time(hour=end_datetime.hour, minute=end_datetime.minute)
        return (start_time, end_time)
