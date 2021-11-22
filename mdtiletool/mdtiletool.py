#!/usr/bin/env python3
# mdtiletool.py
#
# Copyright © 2021 Ben Sampson <github.com/billyrayvalentine>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
#
# Requires Python >= 3.6
"""A Commandline util to covert an image into assembly for the Sega MegaDrive"""

import sys
import logging
import argparse
from PIL import Image

# The transparent colour is set to black and is the first colour in the palette
TRANSPARENT_COLOUR = (0x00, 0x00, 0x00)

def check_is_factor_of_eight(image):
    """Check if image is divisible by 8, return tuple of pixels (x,y) which
    that should be cropped

    A returned tuple of (0,0) means image is divisible by eight"""
    dim = image.size

    logging.debug(f'Image is {dim}')

    return (dim[0] % 8, dim[1] % 8)

def auto_reduce_colours(image, colours=15):
    """Try and automatically reduce the colours to 15"""
    return image.convert(mode='P', palette=Image.ADAPTIVE, colors=colours)

def count_colours(image):
    """Return the number of colours in the image - only works when the image
    has been converted to a 'P' mode"""
    return len(image.getcolors())

def get_palette(image, colours=15):
    """Return the used colours from the palette in the format:
        [
            (R, G, B),
            (R, G, B)
        ]
    """
    # getpalette() always seems to return a palette of 256 entries regardless
    # of how many are used so strip out the number of colours used which luckerly
    # is the items at the top of the list
    used_colours = image.getpalette()[:colours * 3]

    # format the stream of values into a nice format
    formatted_palette = []
    # Add the transparent colour to the top of the palette
    formatted_palette.append(TRANSPARENT_COLOUR)
    col = 0
    while col < len(used_colours):
        formatted_palette.append((used_colours[col], used_colours[col + 1], used_colours[col + 2]))
        col += 3

    return formatted_palette

def print_palette(palette, name='Palette0'):
    """Print a formatted palette in GNU AS assembly format

    Args:
        palette:
            A palette formatted using get_palette
        name:
            Name of the Palette to print in the assembly DEFAULT='Palette0'
    """
    print(f'{name}:')
    for colour in palette:
        r, g, b = colour[0], colour[1], colour[2]
        print(f'  .word 0x{rgb_to_megadrive_vdp(r, g, b):04X}')

def rgb_to_megadrive_vdp(red, green, blue):
    """Convert a 24bit RGB value into the 12 bit long 3bit/colour format used by the
    megadrive VDP in the format of:

    BBB0 GGG0 RRR0

    Args:
        red, green, blue:
            8bit integer values used to represent a colour between 0-255
    Returns:
        A 12bit integer formatted for use with the megadrive VDP

    Raises:
        ValueError: If red, green or blue is not 0-255

    """
    if red > 255 or green > 255 or blue > 255:
        raise ValueError

    if red < 0 or green < 0 or blue < 0:
        raise ValueError

    # Shift the colour to strip to 3bits then shift into the required format
    blue_formatted = (blue >> 5) << 9 # 0bBBB000000000
    green_formatted = (green >> 5) << 5 # 0bGGG00000
    red_formatted = (red >> 5) << 1 # 0bRRR0

    # Mask colours together to give the formatted colour
    return blue_formatted | green_formatted | red_formatted

def print_tiles(image, name='Image0'):
    """Convert the image into tiles that can be loaded by assembler

    Args:
        image:
            image to generate tiles for
        name:
            Name of the Palette to print in the assembly DEFAULT='Image0'
    """
    x_tile_offset = 0
    y_tile_offset = 0

    cols = int(image.width / 8)
    rows = int(image.height / 8)

    print(f'{name}:')
    for row in range(0, rows):
        x_tile_offset = 0
        logging.debug(f'on row {row} tile y_offset = {y_tile_offset}')
        for col in range(0, cols):
            logging.debug(f'on col {col} tile x_offset = {x_tile_offset}')
            for y in range(0, 8):
                print('  .long 0x', end="")
                for x in range(0, 8):
                    # Get pixel will return the index of the palette colour used
                    # Used at the give pixel.  Add 1 to it as the TRANSPARENT_COLOUR
                    # has been set in the palette already
                    logging.debug(f'processing {x + x_tile_offset},{y + y_tile_offset}')
                    print(f'{image.getpixel((x + x_tile_offset,y + y_tile_offset))+1 :1X}', end="")
                print('\n', end="")
            print('\n', end="")
            x_tile_offset += 8
        y_tile_offset +=8

if __name__ == '__main__':
    # Setup command line args
    parser = argparse.ArgumentParser(description='mdtiletool')
    parser.add_argument('-d', '--debug', \
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], \
        help='debug level', default='INFO')
    parser.add_argument('image', help='path to image to process')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(format='%(levelname)s %(message)s', \
        level=args.debug)

    logging.debug('Starting app')

    # Main
    # Check the image is a factor of 8
    # Auto reduce it to 15 colours
    # Print the palette and image to STDOUT
    try:
        with Image.open(args.image) as image_fh:
            #print(f'image mode = {image_fh.mode}')
            # check image is a factor of 8
            if check_is_factor_of_eight(image_fh) != (0, 0):
                raise Exception('Image is not a factor of 8 pixels')
            image_fh_reduced = auto_reduce_colours(image_fh)
            palette_formatted = get_palette(image_fh_reduced)
            print_palette(palette_formatted)
            print_tiles(image_fh_reduced)
    except Exception as exception:
        logging.critical(exception)
        sys.exit(1)
