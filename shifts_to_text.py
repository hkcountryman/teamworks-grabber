from PIL import Image, ImageOps
from pytesseract import image_to_string
from typing import Dict, Union

####################################################################################################

def to_text(file: str) -> Dict[int, Union[str, None]]:
    """
    Read and return text from an image.

    Args:
        file: a PNG depicting the week's schedule

    Returns:
        A dictionary mapping numbered days of the week (where 0 is Monday) to string representations
        of my shifts on those days
    """
    divide_days(file)
    shifts = {}
    for i in range(7):
        filename = "tmp_images/tmp" + str(i) + ".png"
        shifts[i] = grab_text(filename)
    return shifts

def divide_days(file: str):
    """
    Given an image of the schedule for a whole week, saves 7 more images in the tmp_images directory,
    1 for each separate day and labeled tmp0.png - tmp6.png, starting with Monday.

    Args:
        file: the PNG depicting the week's schedule
    """
    img = Image.open(file)
    width, height = img.size
    crop_width = width // 7
    # tuple passed to crop() can include left col and top row but not right col or bottom row:
    top = 0
    bottom = height - 1
    for i in range(7):
        left = crop_width * i
        right = crop_width * (i + 1) - 1
        filename = "tmp_images/tmp" + str(i) + ".png"
        img.crop((left, top, right, bottom)).save(filename)

def extract_content(file: str) -> Image:
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
    # tuple passed to crop() can include left col and top row but not right col or bottom row:
    left = 0
    top = border
    right = width - 1
    bottom = height - 1
    lower_section = img.crop((left, top, right, bottom))
    # invert just the lower section if necessary:
    center = tuple(pixel // 2 for pixel in lower_section.size)
    center_pixel = lower_section.getpixel(center)
    if center_pixel == (0, 128, 0): # Tesseract has problems reading white on green; must invert
        negative = invert(lower_section)
        return negative
    else:
        return lower_section

def invert(pic: Image) -> Image:
    """
    Inverts the colors in an image because Tesseract doesn't play nice with light text on dark.

    Args:
        pic: PIL.Image object to invert

    Returns:
        The negative PIL.Image object
    """
    return ImageOps.invert(pic) # negative colors

def grab_text(file: str) -> str:
    img = extract_content(file)
    full_text = image_to_string(img)
    shift = full_text.split("\n")[0] # my shift is on the first line of full text read by Tesseract
    if shift == "\x0c": # blank string read by Tesseract
        return None
    else:
        return shift

print(to_text("tmp_images/tmp.png"))
