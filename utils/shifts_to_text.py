from dataclasses import astuple
from typing import List, Union

from pathlib import Path
from PIL import Image, ImageOps
from pytesseract import image_to_string

from .CropBox import CropBox

####################################################################################################

DAYS_IN_WEEK = 7
BRIGHT_GREEN = (0, 128, 0) # RGB value for the green on the schedule

def date(file: Union[Path, str]) -> int:
    """
    Get the number of the first day of the week (Monday).

    Args:
        file: a PNG depicting the week's schedule

    Returns:
        The number of the day
    """
    img = Image.open(file)
    width, height = img.size
    boundaries = CropBox(left=0, top=0, right=width//7, bottom=height//3)
    monday = img.crop(astuple(boundaries)) # extract portion of calendar with Monday
    date = image_to_string(monday)
    return int("".join(filter(str.isdigit, date)))

def shifts(file: Union[Path, str]) -> List[Union[str, None]]:
    """
    Read and return a list of the text from each shift in a week.

    Args:
        file: a PNG depicting the week's schedule

    Returns:
        A dictionary mapping numbered days of the week (where 0 is Monday) to string representations
        of my shifts on those days
    """
    divide_days(file)
    return [get_shift(f"tmp_images/tmp{x}.png") for x in range(7)]

def divide_days(file: Union[Path, str]):
    """
    Given an image of the schedule for a whole week, saves 7 images in the tmp_images directory, 1
    for each separate day and labeled tmp0.png - tmp6.png, starting with Monday.

    Args:
        file: the PNG depicting the week's schedule
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
    """
    Given an image of the schedule for a single day, crops the image to only contain the lower
    portion so that it shows the scheduled shift but not the date. If the scheduled shift appears
    against a green background, the image is then inverted to make it easier for the OCR to read.

    Args:
        file: the PNG depicting the day's schedule

    Returns:
        The cropped (and possibly inverted) PIL.Image object
    """
    img = Image.open(file)
    width, height = img.size
    border = height // 3 # border where lower section starts
    boundaries = CropBox(left=0, top=border, right=width-1, bottom=height-1) # boundaries to crop
    lower_section = img.crop(astuple(boundaries))
    # check if the image is white text on a green background:
    center = tuple(pixel // 2 for pixel in lower_section.size)
    center_pixel = lower_section.getpixel(center)
    # Tesseract has problems reading white text on green; may need to invert:
    return ImageOps.invert(lower_section) if center_pixel == BRIGHT_GREEN else lower_section

def get_shift(file: Union[Path, str]) -> Union[str, None]:
    """
    Given an image of the schedule for a single day, read the scheduled shift from the image.

    Args:
        file: the PNG depicting the day's schedule

    Returns:
        A string with the start and end times of the scheduled shift, or None on a day off.
    """
    shift = image_to_string(extract_content(file)).split("\n")[0] # my shift
    if shift[0] == "(": # for some reason Tesseract sees a "(" in front of leading "0" characters
        shift = shift[1:] # so we simply cut the "("
    return None if shift == "\x0c" else shift # \x0c is a whitespace constant for days with no shift
