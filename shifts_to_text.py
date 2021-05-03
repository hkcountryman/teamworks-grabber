from CropBox import CropBox
from dataclasses import astuple
from pathlib import Path
from PIL import Image, ImageOps
from pytesseract import image_to_string
from typing import List, Union
####################################################################################################

DAYS_IN_WEEK = 7
BRIGHT_GREEN = (0, 128, 0) # RGB value for the green on the schedule
#monday_date = 0 # day of the month of the first day in the schedule

def to_text(file : Union[Path, str]) -> List[Union[str, None]]:
    """
    Read and return a list of the text from each shift in a week.

    Args:
        file: a PNG depicting the week's schedule

    Returns:
        A dictionary mapping numbered days of the week (where 0 is Monday) to string representations
        of my shifts on those days
    """
    divide_days(file)
    '''shifts = []
    for i in range(7):
        if i == 0:
            shifts[i] = grab_text(f"tmp_images/tmp{i}.png", monday=True)
        else:
            shifts[i] = grab_text(f"tmp_images/tmp{i}.png")'''
    return [grab_text(f"tmp_images/tmp{x}.png") for x in range(7)]

def divide_days(file : Union[Path, str]):
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
    '''if monday: # if we are looking at Monday, get the number of the month out
        boundaries = CropBox(left=0, top=0, right=width-1, bottom=border) # boundaries to crop
        upper_section = img.crop(astuple(boundaries))
        monday_date = int("".join(filter(str.isdigit, image_to_string(upper_section))))'''
    boundaries = CropBox(left=0, top=border, right=width-1, bottom=height-1) # boundaries to crop
    lower_section = img.crop(astuple(boundaries))
    # check if the image is white text on a green background:
    center = tuple(pixel // 2 for pixel in lower_section.size)
    center_pixel = lower_section.getpixel(center)
    # Tesseract has problems reading white text on green; may need to invert:
    return ImageOps.invert(lower_section) if center_pixel == BRIGHT_GREEN else lower_section

def grab_text(file : Union[Path, str]) -> Union[str, None]:
    """
    Given an image of the schedule for a single day, read the scheduled shift from the image.

    Args:
        file: the PNG depicting the day's schedule

    Returns:
        A string with the start and end times of the scheduled shift, or None on a day off.
    """
    shift = image_to_string(extract_content(file)).split("\n")[0] # my shift
    return None if shift == "\x0c" else shift # \x0c is a whitespace constant for days with no shift

print(to_text("tmp_images/tmp.png"))