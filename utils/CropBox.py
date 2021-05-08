from dataclasses import dataclass

@dataclass
class CropBox:
    """This gives the pixel boundaries needed by PIL.Image.crop() to crop a section of an Image
    object. Note that they are inclusive of the left column and top row boundaries but exclusive of
    the right column and bottom row boundaries. It should be converted into a tuple before use.
    """
    left : int
    top : int
    right : int
    bottom : int
