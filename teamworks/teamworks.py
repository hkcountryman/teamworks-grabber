#!/usr/bin/env python3

import configparser
import os
from os.path import dirname, exists, join

def make_img_dir() -> str:
    img_dir = join(dirname(__file__), "tmp_images")
    if not exists(img_dir):
        os.makedirs(img_dir)
    return str(img_dir)

def printscreen():
    save_as = join(make_img_dir(), "tmp.png")
    config_file = join(dirname(__file__), "config.ini")
    config = configparser.ConfigParser()
    config.read(config_file)
    command = f"{config['cli']['screenshotter']} {config['cli']['args']} {save_as}"
    os.system(command)

if __name__ == "__main__":
    pass