from dataclasses import astuple
from datetime import datetime, time
from os.path import split
import re
from typing import List, Tuple, Union
from pathlib import Path

from PIL import Image, ImageOps
from pytesseract import image_to_string

from .CropBox import CropBox

DAYS_IN_WEEK = 7
BRIGHT_GREEN = (0, 128, 0) # RGB value for the green on the schedule
WHITE = (255, 255, 255) # RGB value for white

def shifts(file: Union[Path, str]) -> List[Tuple[Union[time, None]]]:
    """Read and return a list of the text from each shift in a week.

    Args:
        file: A PNG depicting the week's schedule.

    Returns:
        A list of shifts as tupples with start and end times (or None for no shift), starting with
        Monday's shift.
    """
    # Save each day as its own image:
    divide_days(file)
    # Extract shifts as strings:
    shifts = [get_shift(f"tmp_images/tmp{x}.png") for x in range(DAYS_IN_WEEK)]
    # Convert to list of paired time objects:
    return [shift_to_tuple(x) for x in shifts]

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

def invert(file: Union[Path, str]) -> Image.Image:
    """Given an image of the schedule for a single day, if the scheduled shift appears against a
    green background, inverts the image to make it easier for the OCR to read.

    Args:
        file: The PNG depicting the day's schedule.

    Returns:
        The Image object, potentially inverted.
    """
    img = Image.open(file).convert("RGB")
    # Check if the image is white text on a green background:
    center = tuple(pixel // 2 for pixel in img.size)
    center_pixel = img.getpixel(center)
    # Tesseract has problems reading white text on green; may need to invert:
    return ImageOps.invert(img) if center_pixel == BRIGHT_GREEN else img

def get_shift_(file: Union[Path, str]) -> Union[str, None]:
    """Given an image of the schedule for a single day, read the scheduled shift from the image.

    Args:
        file: The PNG depicting the day's schedule.

    Returns:
        A string with the start and end times of the scheduled shift, or None on a day off.
    """
    shift = image_to_string(invert(file)).split("\n")[0] # my shift
    # Occasionally Tesseract mistakenly sees the following characters at the beginning or end of the
    # shift strings:
    if shift[0] == "(" or shift[0] == "{":
        shift = shift[1:]
    if shift[-1] == ".":
        shift = shift[:-1]
    return None if shift == "\x0c" else shift # \x0c is a whitespace constant for days with no shift

def split_by_coverage(file: Union[Path, str]) -> Tuple[Image.Image, Union[Image.Image, None]]:
    """Given an image of the schedule for a single day, detects whether it includes multiple
    coverage types and splits the image into the corresponding sections if so. Assumes no more than
    two types of coverage per shift.

    Args:
        file: The PNG depicting the day's schedule.

    Returns:
        A tuple containing one or two images, for one or two types of coverage, respectively.
    """
    # what happens on days with no shift?
    img = Image.open(file).convert("RGB")
    width, height = img.size
    for y in range(height):
        test_pixel = (2*width//3, y) # pixel to check color of current row
        # Search for first colored row:
        if not img.getpixel(test_pixel) == WHITE:
            first_color = img.getpixel(test_pixel)
            first_row = y
    # Search through colored rows:
    dividing_row = None
    for y in range(first_row, height):
        test_pixel = (2*width//3, y) # pixel to check color of current row
        # Search for dividing line:
        if not img.getpixel(test_pixel) == first_color:
            dividing_row = y
    # In the case of one type of coverage:
    if dividing_row == None:
        return (img, None)
    # In the case of two types of coverage:
    boundaries1 = CropBox(left=0, top=0, right=width-1, bottom=dividing_row)
    img1 = img.crop(astuple(boundaries1)).convert("RGB") # upper coverage crop
    boundaries2 = CropBox(left=0, top=dividing_row, right=width-1, bottom=height-1)
    img2 = img.crop(astuple(boundaries2)).convert("RGB") # lower coverage crop
    return (img1, img2)

def read_shift_text(img: Image.Image) -> Union[str, None]:
    """Given an image of a coverage block, read the scheduled shift from the image.

    Args:
        img: The PNG depicting a portion of coverage.

    Returns:
        A string with the start and end times of the scheduled shift, or None on a day off.
    """
    width, height = img.size
    test_pixel = (2*width//3, height//2) # pixel to check color of shift
    # Tesseract has problems reading white text on green; may need to invert:
    if img.getpixel(test_pixel) == BRIGHT_GREEN:
        img = ImageOps.invert(img)
    shift = image_to_string(img).split("\n")[0] # shift start and end times as string
    # Occasionally Tesseract mistakenly sees the following characters at the beginning or end of the
    # shift strings:
    if shift[0] == "(" or shift[0] == "{":
        shift = shift[1:]
    if shift[-1] == ".":
        shift = shift[:-1]
    return None if shift == "\x0c" else shift # \x0c is a whitespace constant for days with no shift

def get_shift(file: Union[Path, str]) -> Union[str, None]:
    """Given an image of the schedule for a single day, read the scheduled shift from the image if
    there is one. If a shift has two separate types of coverage, each is read individually and the
    full shift as a string is constructed from the two coverage blocks.

    Args:
        file: The PNG depicting the day's schedule.

    Returns:
        A string with the start and end times of the scheduled shift, or None on a day off.
    """
    img1, img2 = split_by_coverage(file)
    # There will always be at least one type of coverage per shift, regardless:
    coverage1 = read_shift_text(img1)
    # In the case of a day with no shift:
    if coverage1 == None:
        return None
    # In the case of a shift of one coverage type:
    if img2 == None:
        return coverage1
    # In the case of a shift of two coverage types:
    else:
        coverage2 = read_shift_text(img2)
        start_time = re.compile(r"\d\d:\d\d").findall(coverage1)[0]
        end_time = re.compile(r"\d\d:\d\d").findall(coverage2)[1]
        return f"{start_time} - {end_time}"
        

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
